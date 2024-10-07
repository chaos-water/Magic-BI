from magic_bi.config.base_config import BaseConfig

language_code_2_language_name = {"en": "English", "zh": "Chinese"}

class MiscConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.language_code: str = ""

    def get_language_name(self) -> str:
        return language_code_2_language_name.get(self.language_code, "Chinese")

