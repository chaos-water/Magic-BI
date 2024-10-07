from magic_bi.config.model_config import ModelConfig
from loguru import logger
# from transformers import AutoModelForCausalLM, AutoTokenizer
from openai import OpenAI
from magic_bi.model.base_llm_adapter import BaseLlmAdapter

from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info

# default: Load the model on the available device(s)
# model = Qwen2VLForConditionalGeneration.from_pretrained(
#     "Qwen/Qwen2-VL-72B-Instruct", torch_dtype="auto", device_map="auto"
# )
# processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-72B-Instruct")
# We recommend enabling flash_attention_2 for better acceleration and memory saving, especially in multi-image and video scenarios.
# model = Qwen2VLForConditionalGeneration.from_pretrained(
#     "Qwen/Qwen2-VL-72B-Instruct",
#     torch_dtype=torch.bfloat16,
#     attn_implementation="flash_attention_2",
#     device_map="auto",
# )

# default processer


# The default range for the number of visual tokens per image in the model is 4-16384. You can set min_pixels and max_pixels according to your needs, such as a token count range of 256-1280, to balance speed and memory usage.
# min_pixels = 256*28*28
# max_pixels = 1280*28*28
# processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-72B-Instruct", min_pixels=min_pixels, max_pixels=max_pixels)



class QwenVlAdapter(BaseLlmAdapter):
    def __init__(self):
        self.client = None
        self.model_config: ModelConfig = None

    def init(self, model_config: ModelConfig) -> int:
        self.model_config = model_config
        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
            model_config.model, torch_dtype="auto", device_map="auto"
        )
        self.processor = AutoProcessor.from_pretrained(model_config.model)

        logger.debug("OpenaiAdapter init suc")
        return 0

    def process(self, user_input_text: str, user_input_image: bytes, temperature = 0) -> str:
        from magic_bi.utils.utils import image_bytes_to_base64
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": image_bytes_to_base64(user_input_image),
                    },
                    {"type": "text", "text": user_input_text},
                ],
            }
        ]

        # Preparation for inference
        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        inputs = inputs.to("cuda")

        # Inference: Generation of the output
        generated_ids = self.model.generate(**inputs, max_new_tokens=128)
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = self.processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )
        print(output_text)
        logger.debug("process suc, output_text_cnt: %d" % len(output_text))
        return output_text


    def get_model_config(self) -> ModelConfig:
        return self.model_config


if __name__ == "__main__":
    model_config: ModelConfig = ModelConfig()
    model_config.model = ""

    qwen_vl_adapter = QwenVlAdapter()
    qwen_vl_adapter.init(model_config=model_config)

    qwen_vl_adapter.process()
