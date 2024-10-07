from magic_bi.config.base_config import BaseConfig

class QdrantConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.host: str = ""
        self.port: str = ""
