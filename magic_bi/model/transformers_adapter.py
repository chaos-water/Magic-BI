import transformers
import torch
from loguru import logger

class ModelConfig():
    def __init__(self):
        self.vendor: str = ""
        self.api_key: str = ""
        self.base_url: str = ""
        self.model: str = ""    # model name or model path
        self.system_prompt: str = ""
        self.context_size: int = 0
        self.max_new_tokens: int = 0

class TransformersAdapter:
    def __init__(self):
        self.pipeline = None
        self.model_config: ModelConfig = None

    def init(self, model_config: ModelConfig) -> int:
        self.pipeline = transformers.pipeline(
            "text-generation",
            model=model_config.model,
            model_kwargs={"torch_dtype": torch.bfloat16},
            device_map="auto",
        )

        logger.debug("init suc")
        return 0

    def process(self, user_input) -> str:
        outputs = self.pipeline(
            user_input,
            max_new_tokens=self.model_config.max_new_tokens
        )

        output = outputs[0]["generated_text"][-1]

        logger.debug("process, output is %d", len(output))
        return output

# if __name__ == "__main__":
#     model_config = ModelConfig()
#     model_config.model = "/data/guangkuan_init_model"
#     # model_path = ""
#     transformers_adapter = TransformersAdapter()
#     transformers_adapter.init(model_config)
#     transformers_adapter.process(prompt)

