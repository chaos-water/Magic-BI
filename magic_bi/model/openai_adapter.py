from magic_bi.config.model_config import ModelConfig
from loguru import logger
# from transformers import AutoModelForCausalLM, AutoTokenizer
from openai import OpenAI
from magic_bi.model.base_llm_adapter import BaseLlmAdapter


class OpenaiAdapter(BaseLlmAdapter):
    def __init__(self):
        self.client = None
        self.model_config: ModelConfig = None

    def init(self, model_config: ModelConfig) -> int:
        self.model_config = model_config
        self.client = OpenAI(
            api_key=model_config.api_key,
            base_url=model_config.base_url,
        )

        logger.debug("OpenaiAdapter init suc")
        return 0

    def process(self, user_input: str, image_bytes: bytes = None, temperature = 0) -> str:
        messages = [
            {
                "role": "system",
                "content": self.model_config.system_prompt
            },
            {
                "role": "user",
                "content": user_input
            }
        ]

        if image_bytes:
            messages.append({
                "role": "user",
                "content": {
                    "image": image_bytes,
                    "text": user_input  # 也可以在这里保持原来的文本
                }
            })

        completion = self.client.chat.completions.create(
            model=self.model_config.model,
            messages=messages,
            temperature=temperature,
        )

        response = completion.choices[0].message.content
        logger.debug("process suc, text_content_cnt: %d" % len(response))
        return response

    def get_model_config(self) -> ModelConfig:
        return self.model_config
