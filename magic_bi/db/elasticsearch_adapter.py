import json

from loguru import logger
from elasticsearch import Elasticsearch, exceptions

from magic_bi.config.elasticsearch_config import ElasticsearchConfig


class ElasticsearchAdapter(object):
    def init(self, elasticsearch_config: ElasticsearchConfig) -> int:
        self.es = Elasticsearch([elasticsearch_config.url], http_auth=(elasticsearch_config.user, elasticsearch_config.password))

        logger.debug("ElasticSearchAdapter init suc")
        return 0

    def create_index(self, index_name) -> int:
        try:
            # 创建索引
            self.es.indices.create(index=index_name)
            logger.debug(f"Index '{index_name}' created successfully.")

        except exceptions.RequestError as e:
            if "resource_already_exists_exception" in str(e):
                logger.error(f"Index '{index_name}' already exists.")
            else:
                logger.error(f"An error occurred: {e}")
                return -1

    def delete_index(self, index_name) -> int:
        try:
            # 删除索引
            self.es.indices.delete(index=index_name)
            logger.debug(f"Index '{index_name}' deleted successfully.")
        except exceptions.NotFoundError:
            logger.error(f"Index '{index_name}' does not exist.")

    def add_document(self, index_name: str, document: dict) -> int:
        try:
            # 添加文档
            res = self.es.index(index=index_name, body=document)
            logger.debug(f"Document added successfully: {res}")
            return 0
        except exceptions.RequestError as e:
            logger.error(f"An error occurred: {e}")
            return -1

    def delete_documents(self, index_name, filter: dict) -> int:
        query = {
            "query": {
                "term": filter
            }
        }

        try:
            # 执行批量删除
            response = self.es.delete_by_query(index=index_name, body=query)
            logger.debug(f"Documents matching %s deleted successfully" % json.dumps(filter))
            return 0
        except exceptions.NotFoundError:
            logger.error(f"No documents found matching %s." % json.dumps(filter))
            return -1
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return -1

    def search(self, index_name: str, query: dict, cnt: int=10) -> dict:
        try:
            res = self.es.search(index=index_name, body=query, size=cnt)
            logger.debug(f"Search results: {res}")
            return res.body
        except exceptions.NotFoundError:
            logger.error(f"Index '{index_name}' does not exist.")
            return {}
        except exceptions.RequestError as e:
            logger.error(f"An error occurred during search: {e}")
            return {}