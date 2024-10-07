from magic_bi.config.base_config import BaseConfig

class OssConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.access_key: str = ""
        self.secret_key: str = ""
        self.endpoint: str = ""
        self.default_bucket: str = "default"
        self.type: str = ""
