from typing import List
from loguru import logger
from sqlalchemy.orm import Session

from magic_bi.db.qdrant_adapter import QdrantPoint
from magic_bi.utils.globals import Globals
# from magic_bi.tools.doc_reader_tool import DocReaderTool
from magic_bi.data.data import Data, DATA_TYPE, get_supported_doc_types, get_supported_image_types, get_supported_video_types
from magic_bi.doc.decode_doc import decode_doc
from magic_bi.doc.text_summarizer import summarize, extract_tags

retrieve_triples_prompt_template = """
[Text To Retrieve]
{text_to_retrieve}

Retrieve as many triples as possible from the above text. Output directly without explanation.
"""

image_describe_prompt_template = \
"""Describe the image detaily in {language_name}."""


class DataManager():
    def __init__(self, globals: Globals, language_name: str):
        self.globals: Globals = globals
        self.language_name = language_name

    def add_doc(self, data: Data) -> int:
        content_chunk_list, full_content = decode_doc(data.name, data.file_bytes, \
                                                      text_embedding=self.globals.text_embedding, \
                                                      openai_adapter=self.globals.general_llm_adapter)

        summary = summarize(full_content, openai_adapter=self.globals.general_llm_adapter)

        qdrant_point: QdrantPoint = QdrantPoint()
        qdrant_point.vector: list = self.globals.text_embedding.get(summary)
        qdrant_point.payload: dict = {"file_id": data.id, "file_name": data.name, "data_type": DATA_TYPE.DOC.value, "summary": summary}
        ret = self.globals.qdrant_adapter.upsert(collection_id=data.dataset_id + "_summary", qdrant_point=qdrant_point)
        if ret != 0:
            logger.error("qdrant upsert failed, dataset_id:")

        chunk_index = 0
        for content_chunk in content_chunk_list:
            qdrant_point: QdrantPoint = QdrantPoint()
            qdrant_point.vector: list = self.globals.text_embedding.get(content_chunk)
            qdrant_point.payload: dict = {"file_id": data.id, "file_name": data.name, "data_type": DATA_TYPE.DOC.value, "chunk_index": chunk_index,
                                          "chunk_content": content_chunk}

            ret = self.globals.qdrant_adapter.upsert(collection_id=data.dataset_id + "_chunk",
                                                     qdrant_point=qdrant_point)
            if ret != 0:
                logger.error("qdrant upsert failed, dataset_id:")

            ret = self.globals.elasticsearch_adapter.add_document(index_name=data.dataset_id,
                                                                  document=qdrant_point.payload)
            if ret != 0:
                logger.error("elasticsearch upsert failed, dataset_id:")

        logger.debug("add_doc suc")
        return 0

    def add_image(self, data: Data) -> int:
        image_describe_prompt = image_describe_prompt_template.replace("{language_name}", self.language_name)
        image_description = self.globals.mllm_adapter.process(image_describe_prompt, data.file_bytes)

        summary = summarize(image_description, openai_adapter=self.globals.general_llm_adapter)

        qdrant_point: QdrantPoint = QdrantPoint()
        qdrant_point.vector: list = self.globals.text_embedding.get(summary)
        qdrant_point.payload: dict = {"file_id": data.id, "file_name": data.name, "data_type": DATA_TYPE.IMAGE.value, "summary": summary}
        ret = self.globals.qdrant_adapter.upsert(collection_id=data.dataset_id + "_summary", qdrant_point=qdrant_point)
        if ret != 0:
            logger.error("qdrant upsert failed, dataset_id:")

        qdrant_point: QdrantPoint = QdrantPoint()
        qdrant_point.vector: list = self.globals.text_embedding.get(image_description)
        qdrant_point.payload: dict = {"file_id": data.id, "file_name": data.name, "data_type": DATA_TYPE.IMAGE.value,
                                      "chunk_content": image_description}

        ret = self.globals.qdrant_adapter.upsert(collection_id=data.dataset_id + "_chunk",
                                                 qdrant_point=qdrant_point)
        if ret != 0:
            logger.error("qdrant upsert failed, dataset_id:")

        ret = self.globals.elasticsearch_adapter.add_document(index_name=data.dataset_id,
                                                              document=qdrant_point.payload)
        if ret != 0:
            logger.error("elasticsearch upsert failed, dataset_id:")

        logger.debug("add_image suc")
        return 0

    def add_video(self, data: Data) -> int:
        logger.debug("add_video suc")
        return 0

    def add(self, data: Data) -> int:
        try:
            with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
                count = session.query(Data).filter(Data.user_id == data.user_id, Data.dataset_id == data.dataset_id,
                                                      Data.name == data.name).count()
                if count > 0:
                    logger.error("add data failed, the same data %s already exists" % data.name)
                    return -1

            file_type = data.name.split(".")[-1]
            if file_type in get_supported_doc_types():
                self.add_doc(data)
            elif file_type in get_supported_image_types():
                self.add_image(data)
            elif file_type in get_supported_video_types():
                self.add_video(data)
            else:
                logger.error("unsupported file_type: %s" % file_type)
                return -1

            if data.type == DATA_TYPE.DOC.value:
                self.globals.oss_factory.add_file(data.id, data.file_bytes, bucket_name=data.dataset_id)

            with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
                session.add(data)
                session.commit()

        except Exception as e:
            logger.error("add data failed")
            logger.error("catch exception:%s" % str(e))
            return -1

        logger.debug("add data suc")
        return 0

    def download(self, data_id: str) -> int:
        self.globals.oss_factory.get_file(data_id)

    def delete(self, data: Data) -> int:
        ret = self.globals.qdrant_adapter.delete_point(data.dataset_id + "_summary", {"file_id": data.id})
        if ret != 0:
            logger.error("qdrant delete failed, dataset_id:%s, data_id:%s" % (data.dataset_id, data.id))

        ret = self.globals.qdrant_adapter.delete_point(data.dataset_id + "_chunk", {"file_id": data.id})
        if ret != 0:
            logger.error("qdrant delete failed, dataset_id:%s, data_id:%s" % (data.dataset_id, data.id))

        ret = self.globals.elasticsearch_adapter.delete_documents(data.dataset_id, {"file_id": data.id})
        if ret != 0:
            logger.error("elasticsearch delete failed, dataset_id:%s, data_id:%s" % (data.dataset_id, data.id))

        with Session(self.globals.sql_orm.engine) as session:
            session.query(Data).filter(Data.id == data.id).delete()
            session.commit()

        logger.debug("delete data suc")
        return 0

    def get(self, user_id: str, dataset_id: str, page_index: int, page_size: int) -> List[Data]:
        if page_index < 1:
            page_index = 1

        offset = (page_index - 1) * page_size
        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            data_list: List[Data] = session.query(Data).filter(Data.user_id == user_id, Data.dataset_id == dataset_id).\
            limit(page_size).offset(offset).all()

        logger.debug("get data suc, data_cnt:%d" % len(data_list))
        return data_list


    def count(self, user_id: str, dataset_id: str) -> int:
        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            count = session.query(Data).filter(Data.user_id == user_id, Data.dataset_id == dataset_id).count()

        logger.debug("count suc, count:%d" % count)
        return count
