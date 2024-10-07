from magic_bi.config.base_config import BaseConfig

class RabbitmqConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.host: str = ""
        self.user: str = ""
        self.password: str = ""
        self.expiration: int = 7200
