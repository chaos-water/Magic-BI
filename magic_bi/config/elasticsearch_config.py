from magic_bi.config.base_config import BaseConfig


class ElasticsearchConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.host: str = ""
        self.port: int = 9200
        self.url: str = ""
        self.user: str = ""
        self.password: str = ""
