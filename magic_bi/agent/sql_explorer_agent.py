from magic_bi.agent.memmory import Memmory
from sqlalchemy.orm import Session
import json
from loguru import logger
from typing import List

from magic_bi.config.agent_config import AgentConfig
from magic_bi.agent.base_agent import BaseAgent
from magic_bi.message.message import Message
from magic_bi.utils.globals import Globals
from magic_bi.io.base_io import BaseIo
from magic_bi.data.data_source import DataSource, DataSourceOrm
from magic_bi.agent.agent_meta import AgentMeta
from magic_bi.agent.utils import get_env_info
from magic_bi.plugin.sql_plugin import SqlPlugin


def decode_llm_output_in_json_list_format(input_text: str) -> list:
    import re
    pattern = re.compile(rf'```json(.*?)```', re.DOTALL)
    matches = pattern.findall(input_text)
    try:
        json_list = json.loads(matches[0].strip())

    except Exception as e:
        logger.error("catch exception:%s" % str(e))
        logger.error("catch exception:%s" % input_text)
        json_list = None

    if json_list is not None and len(json_list) > 0:
        logger.debug("decode_llm_output_in_json_list_format suc, json_list cnt:%d" % len(json_list))
        return json_list

    try:
        input_text = input_text.replace("'", '"')
        json_list = json.loads(input_text)

    except Exception as e:
        logger.error("catch exception:%s" % str(e))
        logger.error("catch exception:%s" % input_text)
        return []

    logger.debug("decode_llm_output_in_json_list_format suc, json_list cnt:%d" % len(json_list))
    return json_list

generate_qa_prompt_template = \
'''{table_descriptions}

First analyze the given conditions, then solve the problem step by step.

Generate a question which you think the above database can answer, the relevant sql statement and the reason why you generate the question.

The question should meet the following conditions as much as possible:
    1, the question has business significance.
    2, the question can be answered by a single table, or it may require the combination of two or three tables.
    3, the question should be in Simple Chinese.

Output in the following format: {"question": "$question", "sql_statement": "$sql_statement", "reason": "$reason"}.'''

generate_qa_prompt_template_v2 = \
'''[Relevant Business]
    {relevant_business}
    
{table_descriptions}

First analyze the given conditions, then solve the problem step by step.

Generate 5 questions which you think the above database can answer and the relevant tables.

The question and table name must meet the following conditions:
    1, the question should have business significance, the above Relevant Business can be referenced but is not limited.
    2, the question can be answered by a single table, or it can be addressed by a combination of two or three tables.
    3, the questions should be as diverse as possible to cover different fields.
    4, the table must be mentioned in the tables above, do not create yourself!

Output in the following format {"question": "$question", "table": ["$table_name"...], "reason": "$reason"} without other explanations.'''

generate_qa_prompt_template_v2_zh = \
'''[Relevant Business]
    {relevant_business}

{table_descriptions}

首先分析给定的条件，然后逐步解决问题。

生成10个你认为上述数据库可以回答的中文问题，以及相关的表。

问题和表名必须满足以下条件：
    1. 问题应具有业务意义，以上相关业务可以参考但不限于此。
    2. 问题可以通过单表回答，也可以通过两到三张表的组合解决。
    3. 问题应尽可能多样化，以覆盖不同领域；不要生成相同或相似的问题。
    4. 表必须在上述表格中提到，不要自行创建！

输出以下格式 [{"question": "$question", "table": ["$table_name"...], "reason": "$reason"}...]，不作其他解释。'''

"""
The question should meet the following conditions as much as possible:
"""

generate_qa_prompt_template_v3 = \
'''[Relevant Business]
    {relevant_business}
    
{table_descriptions}

First analyze the given conditions, then solve the problem step by step.

Generate 10 questions which you think the above database can answer.

The question should meet the following conditions as much as possible:
    1, the question should have business significance, the above Relevant Business can be referenced but is not limited.
    2, the question can be answered by a single table, or it can be addressed by a combination of two or three tables.
    3, the questions should be as diverse as possible to cover different fields.
        
Output in the following format [{"question": "$question", "reason": "$reason"}...] without other explanations.'''

select_table_prompt_template = \
'''{table_descriptions}

[User Question]:
    {user_question}

First analyze the given conditions, then solve the problem step by step.

From the table above, select 1 to 3 tables that you think can answer the user's question.

Output in the following format {"relevant_tables": ["$table_name"...], "reason": "$reason"} without other explanations.'''

"""
From the description of the table above, output the table name that you think can answer the user's question.
"""

generate_sql_prompt_template = \
'''{table_descriptions}

[User Question]:
    {user_question}
    
First analyze the given conditions, then solve the problem step by step.

Generate a sql_statement to query the database to answer the user question. The SQL statement should be successfully executed on the above database.
Output in the following format {"sql_statement": "$sql_statement", "reason": "$reason"} without other explanations.'''

translate_prompt_template = \
"""翻译成简体中文:{input_content}"""

translate_prompt_template_v1 = \
"""[Input Content]:
    {input_content}

If the preceding Input Content is not in Simplified Chinese, translate it into Simplified Chinese; if the preceding text is already in Simplified Chinese, do not process it.
Output without explanation.
"""
evaluate_result_prompt_template = \
'''[User Question]:
    {user_question}

[Sql Statement]:
    {sql_statement}
    
[Sql Result]:
    {sql_result}

First analyze the given conditions, then solve the problem step by step.

Evaluate if the User Question is answered by the Sql Result. The value of is_answered is "yes" or "no".
The criteria for assessment can be slightly lenient, without being overly stringent.
Output in the following format {"is_answered": "$is_answered", "reason": "$reason"} without other explanations.'''


def test_v2():
    from magic_bi.data.data_source import DataSourceOrm, DataSource
    from magic_bi.model.openai_adapter import OpenaiAdapter
    from magic_bi.config.model_config import ModelConfig

    model_config = ModelConfig()
    # model_config.api_key = "sk-XZJS9KxeV23SvOFJ28eINNh8EY5oaBYYPKnPd5M9pxfQW04Z"
    # model_config.model = "moonshot-v1-128k"
    # model_config.base_url = "https://api.moonshot.cn/v1"
    # model_config.system_prompt = "You are a helpful assistant."

    model_config.api_key = "ollama"
    # model_config.model = "llama3.1:70b"
    # model_config.model = "qwen2.5:72b"
    model_config.model = "mistral-large:123b"
    # model_config.base_url = "http://192.168.68.96:11434/v1/"
    model_config.base_url = "http://192.168.68.96:11438/v1/"
    # model_config.base_url = "http://192.168.68.83:11434/v1/"
    model_config.system_prompt = "You are a helpful assistant."

    openai_adapter = OpenaiAdapter()
    openai_adapter.init(model_config=model_config)
    data_source_orm = DataSourceOrm()
    data_source_orm.url = "mysql+pymysql://root:Dmaidaas@10.12.51.162:3306/guangkuan_init"
    data_source = DataSource()
    data_source.init(data_source_orm)
    full_table_list = data_source.get_table_list()
    db_table_description = data_source.get_table_column_batch(table_list=full_table_list, is_mini=True)
    relevant_business = "工单、巡检任务、设备资金、设备、桌面办公、市政数据服务台、设备入库、忙碌&空闲、设备类型、设备数量、运维部门、资产、故障"
    generate_qa_prompt = generate_qa_prompt_template_v2_zh.replace("{table_descriptions}", db_table_description).replace("{relevant_business}", relevant_business)

    index = 0
    while True:
        generate_qa_llm_output = openai_adapter.process(generate_qa_prompt, temperature=0.3)
        print("generate_qa_llm_output: %s" % generate_qa_llm_output)
        try:
            question_dict_list = json.loads(generate_qa_llm_output)
            for question_dict in question_dict_list:
                translated_question = question_dict["question"]
                relevant_tables = question_dict["table"]
                # translate_prompt = translate_prompt_template.replace("{input_content}", question)
                # translated_question = openai_adapter.process(translate_prompt)
                # print("translated_question: %s" % translated_question)

                # select_table_prompt = select_table_prompt_template.replace("{table_descriptions}", db_table_description).replace("{user_question}", translated_question)
                # select_table_llm_output = openai_adapter.process(select_table_prompt)
                # print("select_table_llm_output: %s" % select_table_llm_output)
                # select_table_json = json.loads(select_table_llm_output)
                # relevant_tables = select_table_json["relevant_tables"]
                table_name_wrong_flag = False
                for relevant_table in relevant_tables:
                    if (relevant_table in full_table_list) is False:
                        print("table %s is not in the database" % relevant_table)
                        table_name_wrong_flag = True

                if table_name_wrong_flag is True:
                    continue


                table_descriptions = data_source.get_table_column_batch(relevant_tables)

                generate_sql_prompt = generate_sql_prompt_template.replace("{table_descriptions}", table_descriptions).replace("{user_question}", translated_question)

                generate_sql_llm_output = openai_adapter.process(generate_sql_prompt)
                print("generate_sql_llm_output: %s" % generate_sql_llm_output)
                sql_json = json.loads(generate_sql_llm_output)
                sql_statement = sql_json["sql_statement"]
                from magic_bi.plugin.sql_plugin import SqlPlugin

                sql_plugin = SqlPlugin()
                (ret, sql_output) = sql_plugin.run(sql_statement, data_source.orm.url)
                if ret != 0:
                    print("execute the sql %s failed, the relevant_question is:%s" % (sql_statement, translated_question))
                    continue
                # print("sql_output: %s" % sql_output)
                evaluate_result_prompt = evaluate_result_prompt_template.replace("{user_question}", translated_question).\
                    replace("{sql_result}", sql_output).replace(f"{sql_statement}", sql_statement)
                evaluate_result_llm_output = openai_adapter.process(evaluate_result_prompt)
                print("evaluate_result_llm_output: %s" % evaluate_result_llm_output)
                evaluate_result = json.loads(evaluate_result_llm_output)
                is_answered: str = evaluate_result["is_answered"]
                if is_answered.lower() == "yes":
                    print("00000000000000The question %s is answered successfully, sql:%s" % (translated_question, sql_statement))
                else:
                    print("11111111111111The question %s is answered failed, sql:%s, sql_result:%s" % (translated_question, sql_statement, sql_output))

        except Exception as e:
            print("catch exception:%s" % str(e))

        if index > 20:
            break
        index += 1

def test_v3():
    from magic_bi.data.data_source import DataSourceOrm, DataSource
    from magic_bi.model.openai_adapter import OpenaiAdapter
    from magic_bi.config.model_config import ModelConfig

    model_config = ModelConfig()
    # model_config.api_key = "token-abc123"
    model_config.api_key = "ollama"
    # model_config.model = "llama3.1:70b"
    model_config.model = "qwen2.5:72b"
    # model_config.model = "Meta-Llama-3.1-70B-Instruct-AWQ-INT4"
    model_config.base_url = "http://192.168.68.96:11439/v1/"
    # model_config.model = "llama3.1:405b-instruct-q2_K"
    # model_config.base_url = "http://192.168.68.96:11439/v1/"
    model_config.system_prompt = "You are a helpful assistant."

    openai_adapter = OpenaiAdapter()
    openai_adapter.init(model_config=model_config)
    data_source_orm = DataSourceOrm()
    data_source_orm.url = "mysql+pymysql://root:Dmaidaas@10.12.51.162:3306/guangkuan_init"
    data_source = DataSource()
    data_source.init(data_source_orm)
    full_table_list = data_source.get_table_list()
    db_table_description = data_source.get_table_column_batch(table_list=full_table_list, is_mini=True)
    relevant_business = "工单、巡检任务、设备资金、设备、桌面办公、市政数据服务台、设备入库、忙碌&空闲、设备类型、设备数量、运维部门、资产、故障"
    generate_qa_prompt = generate_qa_prompt_template_v3.replace("{table_descriptions}", db_table_description).replace("{relevant_business}", relevant_business)

    index = 0
    while True:
        generate_qa_llm_output = openai_adapter.process(generate_qa_prompt, temperature=0.3)
        print("generate_qa_llm_output: %s" % generate_qa_llm_output)
        try:
            question_dict_list = json.loads(generate_qa_llm_output)
            for question_dict in question_dict_list:
                question = question_dict["question"]
                translate_prompt = translate_prompt_template.replace("{input_content}", question)
                translated_question = openai_adapter.process(translate_prompt)
                print("translated_question: %s" % translated_question)

                select_table_prompt = select_table_prompt_template.replace("{table_descriptions}", db_table_description).replace("{user_question}", translated_question)
                select_table_llm_output = openai_adapter.process(select_table_prompt)
                print("select_table_llm_output: %s" % select_table_llm_output)
                select_table_json = json.loads(select_table_llm_output)
                relevant_tables = select_table_json["relevant_tables"]
                table_name_wrong_flag = False
                for relevant_table in relevant_tables:
                    if (relevant_table in full_table_list) is False:
                        print("table %s is not in the database" % relevant_table)
                        table_name_wrong_flag = True

                if table_name_wrong_flag is True:
                    continue


                table_descriptions = data_source.get_table_column_batch(relevant_tables)

                generate_sql_prompt = generate_sql_prompt_template.replace("{table_descriptions}", table_descriptions).replace("{user_question}", translated_question)

                generate_sql_llm_output = openai_adapter.process(generate_sql_prompt)
                print("generate_sql_llm_output: %s" % generate_sql_llm_output)
                sql_json = json.loads(generate_sql_llm_output)
                sql_statement = sql_json["sql_statement"]
                from magic_bi.plugin.sql_plugin import SqlPlugin

                sql_plugin = SqlPlugin()
                (ret, sql_output) = sql_plugin.run(sql_statement, data_source.orm.url)
                if ret != 0:
                    print("execute the sql %s failed, the relevant_question is:%s" % (sql_statement, translated_question))
                    continue
                # print("sql_output: %s" % sql_output)
                evaluate_result_prompt = evaluate_result_prompt_template.replace("{user_question}", translated_question).replace("{sql_result}", sql_output)
                evaluate_result_llm_output = openai_adapter.process(evaluate_result_prompt)
                print("evaluate_result_llm_output: %s" % evaluate_result_llm_output)
                evaluate_result = json.loads(evaluate_result_llm_output)
                is_answered: str = evaluate_result["is_answered"]
                if is_answered.lower() == "yes":
                    print("00000000000000The question %s is answered successfully, sql:%s" % (translated_question, sql_statement))
                else:
                    print("11111111111111The question %s is answered failed, sql:%s" % (translated_question, sql_statement))

        except Exception as e:
            print("catch exception:%s" % str(e))

        if index > 20:
            break
        index += 1

if __name__ == '__main__':
    test_v2()