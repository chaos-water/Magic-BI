from magic_bi.config.base_config import BaseConfig


class ModelConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.vendor: str = ""
        self.api_key: str = ""
        self.base_url: str = ""
        self.model: str = ""    # model name or model path
        self.system_prompt: str = ""
        self.context_size: int = 0
        self.max_new_tokens: int = 0
