import uuid
from loguru import logger
from typing import Dict
from qdrant_client.http.models import PointStruct
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams

from magic_bi.config.qdrant_config import QdrantConfig
# from qdrant_client.http.model.md import Filter, FieldCondition, MatchValue

class QdrantPoint():
    def __init__(self):
        self.id: str = uuid.uuid1().hex
        self.vector: list = []
        self.payload: dict = {}

class QdrantAdapter():
    def __init__(self):
        self.client = None

    def init(self, qdrant_config: QdrantConfig) -> int:
        self.client = QdrantClient(host=qdrant_config.host, port=qdrant_config.port)
        logger.debug("QdrantAdapter init suc")
        return 0

    def exit(self):
        self.client.close()

    def get_collections(self):
        try:
            collections = self.client.get_collections()
            logger.debug("list_collection suc, collections=%s" % (collections))
            return 0

        except Exception as e:
            # logger.error("add_collection failed, collection_id:%s, vector_size:%d" % (collection_id, vector_size))
            logger.error("catch exception:%s" % str(e))
            return -1

    def add_collection(self, collection_id: str, vector_size: int):
        try:
            self.client.create_collection(
                collection_name=collection_id,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
            logger.debug("add_collection suc, collection_name=%s, vector_size=%d" % (collection_id, vector_size))
            return 0
        except Exception as e:
            logger.error("add_collection failed, collection_id:%s, vector_size:%d" % (collection_id, vector_size))
            logger.error("catch exception:%s" % str(e))
            return -1

    def is_collection_existed(self, collection_id: str) -> bool:
        try:
            ret = self.client.collection_exists(collection_name=collection_id)

            logger.debug("is_collection_existed suc, ret:%s" % ret)
            return ret
        except Exception as e:
            logger.error("is_collection_existed failed, collection_id:%s" % collection_id)
            logger.error("catch exception:%s" % str(e))
            return False


    def delete_collection(self, collection_id: str):
        try:
            if self.client.collection_exists(collection_name=collection_id):
                self.client.delete_collection(
                    collection_name=collection_id,
                )

            logger.debug("delete_collection suc, collection_id"
                         ""
                         ""
                         ":%s" % collection_id)
            return 0
        except Exception as e:
            logger.error("delete_collection failed, collection_id:%s" % collection_id)
            logger.error("catch exception:%s" % str(e))
            return -1

    def upsert(self, collection_id: str, qdrant_point: QdrantPoint) -> int:
        try:
            points = []
            # for entity in entities:
            point = PointStruct(id=qdrant_point.id, vector=qdrant_point.vector, payload=qdrant_point.payload)
            points.append(point)

            operation_info = self.client.upsert(
                collection_name=collection_id,
                wait=True,
                points=points
            )

            logger.debug("upsert suc, collection_name:%s" % (collection_id))
            return 0
        except Exception as e:
            logger.error("upsert failed, collection_id:%s" % (collection_id))
            logger.error("catch exception:%s" % str(e))
            return -1

#    这段代码是基于qdrant client进行的搜索。我希望做个优化，filter_dict中现有的输入是{"file_id": ""}，我希望这个函数可以支持["file_id": []]
    def search(self, collection_id, input_vector: list, score_threshold: float=0.3, offset=0, cnt=10, filter_dict: dict={}) -> list:
        must_list = []
        for filter_key, filter_value in filter_dict.items():
            # must = model.md.FieldCondition(
            #     key=filter_key,
            #     match=model.md.MatchValue(value=filter_value),
            # )
            if isinstance(filter_value, list):
                # 使用 MatchAny 匹配多个值
                must = models.FieldCondition(
                    key=filter_key,
                    match=models.MatchAny(any=filter_value),
                )
            else:
                # 使用 MatchValue 匹配单个值
                must = models.FieldCondition(
                    key=filter_key,
                    match=models.MatchValue(value=filter_value),
                )
            must_list.append(must)

        try:
            search_results = self.client.search(
                collection_name=collection_id,
                query_vector=input_vector,
                offset=offset,
                limit=cnt,
                score_threshold=score_threshold,
                query_filter=models.Filter(must=must_list)
            )

            logger.debug("search suc, collection_id:%s, score_threshold:%f, cnt:%d" % (collection_id, score_threshold, cnt))
            return search_results
        except Exception as e:
            logger.error("search failed, collection_id:%s, input_vector_size:%d" % (collection_id, len(input_vector)))
            logger.error("catch exception: %s" % str(e))
            return []

    def count(self, collection_id: str) -> int:
        try:
            ret = self.client.count(collection_id=collection_id)

            logger.debug("count suc, collection_name:%s, count:%d" % (collection_id, ret.count))
            return ret.count
        except Exception as e:
            logger.error("count failed, collection_id:%s" % collection_id)
            logger.error("catch exception:%s" % str(e))
            return 0

    def get_points(self, collection_id: str, key_2_value_dict: dict={}) -> list:
        try:
            must_filter_list = []

            for key, value in key_2_value_dict.items():
                must_filter_list.append(models.FieldCondition(
                                                            key=key,
                                                            match=models.MatchValue(value=value),
                                        ))

            results = self.client.scroll(
                collection_name=collection_id,
                scroll_filter=models.Filter(
                    must=must_filter_list
                ),
            )

            logger.debug("get_points suc")
            return results
        except Exception as e:
            logger.error("get_points failed, collection_id:%s, key_2_value_dict:%s" % (collection_id, key_2_value_dict))
            logger.error("catch exception:%s" % str(e))
            return []

    def delete_point(self, collection_id: str, filter_dict: Dict) -> int:
        must = []
        for key, value in filter_dict.items():
            must.append(models.FieldCondition(
                key=key,
                match=models.MatchValue(value=value),
            ))

        filter = models.Filter(must=must)
        try:
            self.client.delete(collection_name=collection_id, points_selector=filter)

            logger.debug("delete_points suc, collection_id:%s, filter_dict:%s" % (collection_id, filter_dict))
            return 0
        except Exception as e:
            logger.error("catch exception %s" % str(e))
            logger.error("delete_points failed, collection_id:%s, filter_dict:%s" % (collection_id, filter_dict))
            return -1

if __name__ == '__main__':
    qdrant_config = QdrantConfig()
    qdrant_config.host = "192.168.68.96"
    qdrant_config.port = 6333
    qdrant_adapter = QdrantAdapter()
    qdrant_adapter.init(qdrant_config)

    data_source_id = "733ae9ac5ec111ef87829c69b4617d12"
    collection_id = data_source_id + "_qa_template"
    results = qdrant_adapter.get_points(collection_id)
    ret = qdrant_adapter.delete_point(collection_id, ["15319bf6-5ed2-11ef-bbae-9c69b4617d12"])
    pass
    # video_chat_results = qdrant_adapter.get_points("video_chat_a9a195302e2511efb09774563c6375f4", {})
    # audio_chat_results = qdrant_adapter.get_points("audio_chat_a9a195302e2511efb09774563c6375f4", {})
    #
    # logger.debug(video_chat_results)
    # logger.debug(audio_chat_results)
    # qdrant_adapter.get_collections()
    # qdrant_adapter.count("zhengqi-chat-demo")
    # qdrant_adapter.delete_collection("zhengqi-chat-demo")
    # qdrant_adapter.delete_collection("documentary-film-clip2")
    # qdrant_adapter.delete_collection("documentary-film-clip3")
