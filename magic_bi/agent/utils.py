import json

from loguru import logger
from typing import List
from magic_bi.data.data_connector import DataConnector
from magic_bi.model.base_llm_adapter import BaseLlmAdapter

def get_relevant_data_connector(llm_adapter: BaseLlmAdapter, person_input: str, authorized_data_connector_list: List):
    prompt_template = \
'''[OPTIONAL DATA CONNECTORS]:
    data_connector_name | data connector url | data connector meta info
    -----------------------
    {provided_data_connectors}

[OUTPUT FORMAT]:
    {"data_connector_name": "data_connector_url"}

[EXAMPLE OUTPUT]:
    {"data_connector_name1": "data_connector_url1", "data_connector_name2": "data_connector_url2"}

[PERSON INPUT]:
    {person_input}

Based on the above, output the data_connectors which are relevant with the person input. Just output the json format data, no other explanation.'''

    def build_prompt(person_input: str, data_connector_list: List[DataConnector]):
        provided_data_connectors = ""
        for data_connector in data_connector_list:
            provided_data_connectors += data_connector.get_meta_info()

        return prompt_template.replace("{person_input}", person_input). \
            replace("{provided_data_connectors}", provided_data_connectors)

    def decode_llm_output(output: str, authorized_data_connector_list: List) -> list[DataConnector]:
        relevant_data_connector_list = []
        try:
            relevant_data_connector_dict = json.loads(output)
            for data_connector in authorized_data_connector_list:
                if data_connector.name in relevant_data_connector_dict:
                    relevant_data_connector_list.append(data_connector)

        except Exception as e:
            pass

        return relevant_data_connector_list

    prompt = build_prompt(person_input, authorized_data_connector_list)
    llm_output = llm_adapter.process(prompt)
    relevant_data_connector_list = decode_llm_output(llm_output, authorized_data_connector_list=authorized_data_connector_list)

    logger.debug("get_relevant_data_connector suc, relevant_data_connector_list cnt:%d" % len(relevant_data_connector_list))
    return relevant_data_connector_list

def get_env_info() -> str:
    env_info = ""

    from magic_bi.utils.utils import generate_formatted_time
    env_info += "Current Time: " + generate_formatted_time()

    return env_info


import json
from magic_bi.model.openai_adapter import OpenaiAdapter

try_divide_question_prompt_template = \
"""[User Questino]
    {user_question}

当用户问题满足以下条件时，将用户问题分解为子问题，并输出多个子问题的合并策略；否则，sub_question和merge_strategy输出为空即可：
    1，涉及不同时间的比较的。

按照以下格式输出{"sub_question":["$sub_question"...], "merge_strategy": "$merge_strategy", "reason": "$reason"}，不需要其它任何解释。

首先分析给定的条件，然后逐步解决问题。"""

merge_sub_question_answer_prompt_template = \
"""[Original User Questino]
    {original_user_question}

{sub_question_answer}

Original User Question被拆分为上诉Sub Question。请合并上诉Sub Question的answer，以回答Original User Question。
按照以下格式输出{"answer":"$answer", "reason": "$reason"}，不需要其它任何解释。

首先分析给定的条件，然后逐步解决问题。"""

def try_divide_user_question(user_question: str, openai_adapter: OpenaiAdapter) -> (list, str):
    try_divide_question_prompt = try_divide_question_prompt_template.replace("{user_question}", user_question)
    llm_output = openai_adapter.process(try_divide_question_prompt)
    try_divide_question = json.loads(llm_output)
    sub_question = try_divide_question["sub_question"]
    merge_strategy = try_divide_question["merge_strategy"]
    return sub_question, merge_strategy

def merge_sub_question_answer(original_user_question: str, sub_question_2_answer_dict: dict, openai_adapter: OpenaiAdapter) -> str:
    merge_sub_question_answer_prompt = merge_sub_question_answer_prompt_template.replace("original_user_question", original_user_question)\
                                             .replace("sub_question_2_answer_dict", json.dumps(sub_question_2_answer_dict))
    llm_output = openai_adapter.process(merge_sub_question_answer_prompt)

    return llm_output