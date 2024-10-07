from magic_bi.config.model_config import ModelConfig
from loguru import logger
# from transformers import AutoModelForCausalLM, AutoTokenizer
from openai import OpenAI


class BaseLlmAdapter():
    def __init__(self):
        pass

    def init(self, model_config: ModelConfig):
        raise NotImplementedError

    def process(self, user_input_text: str, user_input_image: bytes) -> str:
        raise NotImplementedError

    def get_model_config(self) -> ModelConfig:
        raise NotImplementedError