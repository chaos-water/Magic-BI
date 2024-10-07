from magic_bi.config.base_config import BaseConfig

class WebConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.port: int = 0
        self.url_prefix: str = ""
