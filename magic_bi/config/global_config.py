from loguru import logger

from magic_bi.config.system_config import SystemConfig
from magic_bi.config.model_config import ModelConfig
from magic_bi.config.orm_config import OrmConfig
from magic_bi.config.oss_config import OssConfig
from magic_bi.config.qdrant_config import QdrantConfig
from magic_bi.config.elasticsearch_config import ElasticsearchConfig
from magic_bi.config.rabbitmq_config import RabbitmqConfig

class GlobalConfig():
    def __init__(self):
        self.general_llm_config: ModelConfig = ModelConfig()
        self.mllm_config: ModelConfig = ModelConfig()
        self.text2sql_llm_config: ModelConfig = ModelConfig()
        self.text_rerank_config: ModelConfig = ModelConfig()
        self.mllm_config: ModelConfig = ModelConfig()
        self.orm_config: OrmConfig = OrmConfig()
        self.timescale_orm_config: OrmConfig = OrmConfig()
        self.oss_config: OssConfig = OssConfig()
        self.qdrant_config: QdrantConfig = QdrantConfig()
        self.text_embedding_config: ModelConfig = ModelConfig()
        self.elasticsearch_config: ElasticsearchConfig = ElasticsearchConfig()
        self.rabbitmq_config: RabbitmqConfig = RabbitmqConfig()
        self.system_config: SystemConfig = SystemConfig()

    def parse(self, config_file_path: str) -> int:
        from magic_bi.config.utils import get_yaml_content
        yaml_content = get_yaml_content(config_file_path)

        try:
            if len(yaml_content) == 0:
                logger.error("yaml content is blank")
                return -1

            self.orm_config.parse(yaml_content.get("db", {}).get("sql_orm", {}))
            self.timescale_orm_config.parse(yaml_content.get("db", {}).get("timescale_orm", {}))
            self.general_llm_config.parse(yaml_content.get("model", {}).get("general_llm", {}))
            self.mllm_config.parse(yaml_content.get("model", {}).get("mllm", {}))
            self.text2sql_llm_config.parse(yaml_content.get("model", {}).get("text2sql_llm", {}))
            self.text_embedding_config.parse(yaml_content.get("model", {}).get("text_embedding", {}))
            self.text_rerank_config.parse(yaml_content.get("model", {}).get("text_rerank", {}))
            self.oss_config.parse(yaml_content.get("oss", {}))
            self.qdrant_config.parse(yaml_content.get("qdrant", {}))
            self.elasticsearch_config.parse(yaml_content.get("elasticsearch", {}))
            self.rabbitmq_config.parse(yaml_content.get("rabbitmq", {}))
            self.system_config.parse(yaml_content.get("system", {}))

            logger.debug("parse config suc")
            return 0
        except Exception as e:
            logger.error("parse config failed, catch exception:%s" % str(e))
            return -1
