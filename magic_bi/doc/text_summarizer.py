from magic_bi.model.openai_adapter import OpenaiAdapter


summprize_prompt_template = \
"""[Content]
    {content}
Summarize the content, the summarized content is not more than 256. Output without explanation.
"""

generate_tags_prompt_template = \
"""[Content]
    {content}

Generate tags for the content. Not more than 10 tags. Output without explanation.
"""
from loguru import logger

def summarize(input_text: str, openai_adapter: OpenaiAdapter) -> str:
    prompt = summprize_prompt_template.format(content=input_text)
    llm_output = openai_adapter.process(prompt)

    logger.debug("summarize suc")
    return llm_output

def extract_tags(input_text: str, openai_adapter: OpenaiAdapter) -> str:
    prompt = generate_tags_prompt_template.format(content=input_text)
    llm_output = openai_adapter.process(prompt)

    logger.debug("extract_tags: %s", llm_output)
    return llm_output