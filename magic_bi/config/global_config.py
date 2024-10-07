from loguru import logger

from magic_bi.config.misc_config import MiscConfig
from magic_bi.config.model_config import ModelConfig
from magic_bi.config.web_config import WebConfig
from magic_bi.config.agent_config import AgentConfig
# from magic_bi.config.misc_config import MiscConfig
from magic_bi.config.orm_config import OrmConfig
# from magic_bi.config.vector_db_config import VectorDbConfig
from magic_bi.config.oss_config import OssConfig
from magic_bi.config.qdrant_config import QdrantConfig
from magic_bi.config.neo4j_config import Neo4jConfig
from magic_bi.config.elasticsearch_config import ElasticsearchConfig
from magic_bi.config.rabbitmq_config import RabbitmqConfig

class GlobalConfig():
    def __init__(self):
        self.general_llm_config: ModelConfig = ModelConfig()
        self.mllm_config: ModelConfig = ModelConfig()
        self.text2sql_llm_config: ModelConfig = ModelConfig()
        self.text_rerank_config: ModelConfig = ModelConfig()
        self.web_config: WebConfig = WebConfig()
        self.agent_config: AgentConfig = AgentConfig()
        # misc_config: MiscConfig = MiscConfig()
        self.orm_config: OrmConfig = OrmConfig()
        self.timescale_orm_config: OrmConfig = OrmConfig()
        # vector_db_config: VectorDbConfig = VectorDbConfig()
        self.oss_config: OssConfig = OssConfig()
        self.qdrant_config: QdrantConfig = QdrantConfig()
        self.text_embedding_config: ModelConfig = ModelConfig()
        self.neo4j_config: Neo4jConfig = Neo4jConfig()
        self.elasticsearch_config: ElasticsearchConfig = ElasticsearchConfig()
        self.rabbitmq_config: RabbitmqConfig = RabbitmqConfig()
        self.misc_config: MiscConfig = MiscConfig()
        self.rabbitmq_config: RabbitmqConfig = RabbitmqConfig()

    def parse(self, config_file_path: str="./config/magic_bi_local_old.yml") -> int:
        from magic_bi.config.utils import get_yaml_content
        yaml_content = get_yaml_content(config_file_path)

        try:
            if len(yaml_content) == 0:
                logger.error("yaml content is blank")
                return -1

            self.web_config.parse(yaml_content.get("web", {}))

            self.agent_config.parse(yaml_content.get("agent", {}))
            self.orm_config.parse(yaml_content.get("db", {}).get("sql_orm", {}))
            self.timescale_orm_config.parse(yaml_content.get("db", {}).get("timescale_orm", {}))
            self.general_llm_config.parse(yaml_content.get("model", {}).get("general_llm", {}))
            self.general_llm_config.parse(yaml_content.get("mllm", {}).get("mllm", {}))
            self.text2sql_llm_config.parse(yaml_content.get("model", {}).get("text2sql_llm", {}))
            self.text_embedding_config.parse(yaml_content.get("model", {}).get("text_embedding", {}))
            self.text_rerank_config.parse(yaml_content.get("model", {}).get("text_rerank", {}))
            self.oss_config.parse(yaml_content.get("oss", {}))
            self.qdrant_config.parse(yaml_content.get("qdrant", {}))
            self.neo4j_config.parse(yaml_content.get("neo4j", {}))
            self.elasticsearch_config.parse(yaml_content.get("elasticsearch", {}))
            self.rabbitmq_config.parse(yaml_content.get("rabbitmq", {}))

            logger.debug("parse config suc")
            return 0
        except Exception as e:
            logger.error("parse config failed, catch exception:%s" % str(e))
            return -1
