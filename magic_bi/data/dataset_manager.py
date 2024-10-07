from typing import List
from loguru import logger
from sqlalchemy.orm import Session

from magic_bi.utils.globals import Globals
# from magic_bi.tools.doc_reader_tool import DocReaderTool
from magic_bi.data.dataset import Dataset


class DatasetManager():
    def __init__(self, globals: Globals):
        self.globals: Globals = globals

    def add(self, dataset: Dataset) -> int:
        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            count = session.query(Dataset).filter(Dataset.user_id == dataset.user_id, Dataset.name == dataset.name).count()
            if count > 0:
                logger.error("add dataset failed, the same dataset %s already exists" % dataset.name)
                return -1

        ret = self.globals.qdrant_adapter.add_collection(collection_id=dataset.id + "_chunk", vector_size = 768)
        if ret != 0:
            logger.error("add dataset failed, adrant add_collection failed")
            return -1

        ret = self.globals.qdrant_adapter.add_collection(collection_id=dataset.id + "_summary", vector_size = 768)
        if ret != 0:
            logger.error("add dataset failed, adrant add_collection failed")
            return -1

        ret = self.globals.elasticsearch_adapter.create_index(dataset.id)
        if ret != 0:
            logger.error("create elasticsearch adapter %s failed" % dataset.id)

        ret = self.globals.oss_factory.add_bucket(bucket_name=dataset.id)
        if ret != 0:
            logger.error("add dataset failed, oss add_bucket failed")
            return -1

        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            session.add(dataset)
            session.commit()

        logger.debug("add dataset suc")
        return 0


    def delete(self, dataset: Dataset) -> int:
        ret = self.globals.qdrant_adapter.delete_collection(dataset.id + "_chunk")
        if ret != 0:
            logger.error("delete qdrant collection %s failed" % dataset.id)

        ret = self.globals.qdrant_adapter.delete_collection(collection_id=dataset.id + "_summary")
        if ret != 0:
            logger.error("add dataset failed, adrant add_collection failed")
            return -1

        ret = self.globals.qdrant_adapter.delete_collection(collection_id=dataset.id + "_tags")
        if ret != 0:
            logger.error("add dataset failed, adrant add_collection failed")
            return -1

        ret = self.globals.oss_factory.delete_bucket(dataset.id)
        if ret != 0:
            logger.error("delete oss bucket %s failed" % dataset.id)

        ret = self.globals.elasticsearch_adapter.delete_index(dataset.id)
        if ret != 0:
            logger.error("delete elasticsearch adapter %s failed" % dataset.id)

        with Session(self.globals.sql_orm.engine) as session:
            session.query(Dataset).filter(Dataset.id == dataset.id).delete()
            session.commit()

        logger.debug("delete dataset suc")
        return 0

    def get(self, user_id: str) -> List[Dataset]:
        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            dataset_list: List[Dataset] = session.query(Dataset).filter(Dataset.user_id == user_id).all()

        logger.debug("get dataset suc, dataset_cnt:%d" % len(dataset_list))
        return dataset_list

    def count(self, user_id: str) -> int:
        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            total_count = session.query(Dataset).filter(Dataset.user_id == user_id).count()

        logger.debug("count suc, count:%d" % total_count)
        return total_count
