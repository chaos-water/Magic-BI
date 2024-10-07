from loguru import logger

from magic_bi.config.global_config import GlobalConfig
from magic_bi.model.base_llm_adapter import BaseLlmAdapter
from magic_bi.db.sql_orm import SqlOrm
from magic_bi.db.timescale_orm import TimescaleOrm

from magic_bi.oss.oss_factory import OssFactory
from magic_bi.model.text_embedding import TextEmbedding
from magic_bi.db.qdrant_adapter import QdrantAdapter
# from magic_bi.db.neo4j_adapter import Neo4jAdapter
from magic_bi.model.text_reranker_adapter import TextRerankeAdapter
from magic_bi.db.elasticsearch_adapter import ElasticsearchAdapter
from magic_bi.model.openai_adapter import OpenaiAdapter
from magic_bi.mq.rabbitmq_producer import RabbitmqProducer


class Globals():
    def __init__(self):
        self.general_llm_adapter: BaseLlmAdapter = None
        self.mllm_adapter: BaseLlmAdapter = None
        self.text2sql_llm_adapter: BaseLlmAdapter = None
        self.sql_orm: SqlOrm = SqlOrm()
        self.timescale_orm: TimescaleOrm = TimescaleOrm()
        self.oss_factory: OssFactory = OssFactory()
        self.text_embedding: TextEmbedding = TextEmbedding()
        self.text_rerank_adapter: TextRerankeAdapter = TextRerankeAdapter()
        self.qdrant_adapter: QdrantAdapter = QdrantAdapter()
        self.elasticsearch_adapter: ElasticsearchAdapter = ElasticsearchAdapter()
        self.rabbitmq_producer: RabbitmqProducer = RabbitmqProducer()

    def init(self, global_config: GlobalConfig) -> int:
        if global_config.oss_config.loaded:
            ret = self.oss_factory.init(global_config.oss_config)
            if ret != 0:
                logger.error("init oss failed")
                return -1

        if global_config.general_llm_config.loaded:
            self.general_llm_adapter = OpenaiAdapter()

            ret = self.general_llm_adapter.init(global_config.general_llm_config)
            if ret != 0:
                logger.error("init general llm adapter failed")
                return -1

        if global_config.mllm_config.loaded:
            self.mllm_adapter = OpenaiAdapter()

            ret = self.mllm_adapter.init(global_config.mllm_config)
            if ret != 0:
                logger.error("init general llm adapter failed")
                return -1

        if global_config.text2sql_llm_config.loaded:
            self.text2sql_llm_adapter = OpenaiAdapter()

            ret = self.text2sql_llm_adapter.init(global_config.text2sql_llm_config)
            if ret != 0:
                logger.error("init text2sql llm adapter failed")
                return -1

        if global_config.orm_config.loaded:
            ret = self.sql_orm.init(global_config.orm_config.url)
            if ret != 0:
                logger.error("init orm failed")
                return -1

        if global_config.text_embedding_config.loaded:
            ret = self.text_embedding.init(global_config.text_embedding_config)
            if ret != 0:
                logger.error("init text embedding failed")
                return -1

        if global_config.text_rerank_config.loaded:
            ret = self.text_rerank_adapter.init(global_config.text_rerank_config.model)
            if ret != 0:
                logger.error("init text rerank failed")
                return -1

        if global_config.qdrant_config.loaded:
            ret = self.qdrant_adapter.init(global_config.qdrant_config)
            if ret != 0:
                logger.error("init qdrant adapter failed")
                return -1

        if global_config.elasticsearch_config.loaded:
            ret = self.elasticsearch_adapter.init(global_config.elasticsearch_config)
            if ret != 0:
                logger.error("init elasticsearch_adapter failed")
                return -1

        if global_config.timescale_orm_config.loaded:
            ret = self.timescale_orm.init(global_config.timescale_orm_config.url)
            if ret != 0:
                logger.error("init timescale adapter failed")
                return -1

        if global_config.rabbitmq_config.loaded:
            ret = self.rabbitmq_producer.init(global_config.rabbitmq_config)
            if ret != 0:
                logger.error("init rabbitmq producer failed")
                return -1

        logger.debug("init suc")
        return 0


GLOBAL_CONFIG = GlobalConfig()
GLOBALS = Globals()
