from magic_bi.config.base_config import BaseConfig

class Neo4jConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.uri: str = ""
