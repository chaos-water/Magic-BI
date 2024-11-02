from magic_bi.config.base_config import BaseConfig


language_code_2_language_name = {"en": "English", "zh": "Chinese"}

class SystemConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.root_dir: str = ""
        self.model_identity: str = ""
        self.model_creator: str = ""

        self.port: int = 0
        self.url_prefix: str = ""

        self.language_code: str = ""

        self.memmory_enabled: bool = False

    def get_language_name(self) -> str:
        return language_code_2_language_name.get(self.language_code, "Chinese")