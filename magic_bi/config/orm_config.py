from magic_bi.config.base_config import BaseConfig

class OrmConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.url: str = ""
        self.host: str = ""
        self.port: str = ""
        self.user: str = ""
        self.password: str = ""
        self.database: str = ""
