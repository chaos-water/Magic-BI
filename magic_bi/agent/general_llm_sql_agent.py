from magic_bi.agent.memmory import Memmory
from sqlalchemy.orm import Session
import json
from loguru import logger
from typing import List

from magic_bi.agent.base_agent import BaseAgent
# from magic_bi.message.llm_transaction import LlmTransaction
from magic_bi.message.message import Message
from magic_bi.utils.globals import Globals
from magic_bi.io.base_io import BaseIo
from magic_bi.data.data_source import DataSource
# from magic_bi.data.data import Data, DATA_TYPE
from magic_bi.agent.agent_meta import AgentMeta
# from magic_bi.model.base_llm_adapter import BaseLlmAdapter
# from magic_bi.utils.globals import GLOBALS
from magic_bi.agent.utils import get_env_info
from magic_bi.data.data_source import get_qa_template_embedding_collection_id, get_table_description_embedding_collection_id, get_domain_knowledge_embedding_collection_id
# from magic_bi.message.llm_transaction import LlmTransaction, LLM_TRANSACTION_TYPE

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
        json_list = json.loads(input_text)

    except Exception as e:
        logger.error("catch exception:%s" % str(e))
        logger.error("catch exception:%s" % input_text)
        return []

    logger.debug("decode_llm_output_in_json_list_format suc, json_list cnt:%d" % len(json_list))
    return json_list

select_tables_from_referenced_sql_prompt_template = \
'''[Referenced Sql Statements]:
{referenced_sql_statements}

Identify the table names from the SQL statements.
Output the tables in json list format directly without any explanation. Eg: [""].
'''

select_tables_from_full_table_prompt_template = \
'''[Database Table Names]:
{database_table_names}

[Relevant Table Descriptions]:
{relevant_table_descriptions}

[User Question]:
{user_question}

Identify the tables from [Database Table Names] that you think may answer the user's question.
Output the tables in json list format directly without any explanation. Eg: [""].
'''

generate_sql_prompt_template = \
'''[Env Info]:
{env_info}

{relevant_table_column}

[User Table Descriptions]:
{user_table_descriptions}

[User Domain Knowledge]:
{user_domain_knowledge}

[Referenced SQL statement]:
{referenced_sql_statements}

[User Question]:
{user_question}

Based on the above, generate sql that answer the user question by the db.
Directly output the SQL statement without any explanation.
'''

def decode_llm_output_query_data(output: str) -> str:
    python_code = output
    from magic_bi.plugin.python_plugin import PythonPlugin

    python_plugin = PythonPlugin()
    plugin_output = python_plugin.run(python_code)

    logger.debug("decode_llm_output suc")
    return plugin_output

prompt_template_make_sql_output_human_readable = \
'''[USER INPUT]:
    {user_input}

[RETRIEVED DATA]:
    {retrieved_data}

根据抽取的数据用简体中文回答用户问题，不要提类似于“根据”的词。
'''

def build_prompt_make_sql_output_human_readable(person_input: str, retrieved_data: str, memmory: str = ""):
    # prompt = prompt_template_answer_user.format(user_input=person_input, retrieved_data=retrieved_data, memmory=memmory)
    prompt = prompt_template_make_sql_output_human_readable.format(user_input=person_input, retrieved_data=retrieved_data)
    return prompt

def decode_llm_output_answer_user(output: str) -> str:
    output = output.strip("'''").lstrip("python")
    return output

class GeneralLlmSqlAgent(BaseAgent):
    def __init__(self):
        self.memmory: Memmory = Memmory()
        super().__init__()

    def init(self, agent_meta: AgentMeta, globals: Globals, io: BaseIo) -> int:
        super().init(agent_meta, globals, io)
        self.memmory.init(globals=globals, agent_id=agent_meta.id, context_size=globals.general_llm_adapter.get_model_config().context_size)

        logger.debug("init suc")
        return 0

    def process_v1(self, message: Message) -> str:
        data_source: DataSource = self.get_data_source(self.agent_meta.user_id, message.data_source_id)
        if data_source is None:
            logger.error("process failed, relevant_data_source_list cnt is 0")
            return "", "", "", ""

        sql_output, human_readable_output, sql_cmd, few_shot_examples = self.process_in_few_shot_examples_mode(message, data_source)
        if sql_output != "":
            logger.debug("process suc")
            return sql_output, human_readable_output, sql_cmd, few_shot_examples

        sql_output, human_readable_output, sql_cmd, few_shot_examples = self.process_in_free_mode(message, data_source)

        logger.debug("process suc")
        return sql_output, human_readable_output, sql_cmd, few_shot_examples

    # def get_env_info(self) -> str:
    #     env_info = ""
    #
    #     from magic_bi.utils.utils import generate_formatted_time
    #     env_info += "Current Time: " + generate_formatted_time()
    #
    #     return env_info

    def get_relevant_tables(self, person_input: str, data_source: DataSource, relevant_table_descriptions: str, relevant_domain_knowledge: str,
                            relevant_qa_template: str, message_id: str) -> (list, list):
        full_table_names = data_source.get_table_list()

        select_tables_from_refecenced_sql_prompt = select_tables_from_referenced_sql_prompt_template.replace(
            "{database_table_names}", str(full_table_names)).replace("{relevant_table_descriptions}",
                                                                     str(relevant_table_descriptions)). \
            replace("{domain_knowledge}", str(relevant_domain_knowledge)).replace("{referenced_sql_statements}",
                                                                                  str(relevant_qa_template)).replace(
            "{user_question}", person_input)

        table_list_from_referenced_sql_str = self.globals.general_llm_adapter.process(select_tables_from_refecenced_sql_prompt)
        table_list_from_referenced_sql = decode_llm_output_in_json_list_format(table_list_from_referenced_sql_str)

        select_tables_by_llm_guess_prompt = select_tables_from_full_table_prompt_template.replace(
            "{database_table_names}", str(full_table_names)).replace("{relevant_table_descriptions}",
                                                                     str(relevant_table_descriptions)). \
            replace("{domain_knowledge}", str(relevant_domain_knowledge)).replace(
            "{user_question}", person_input)

        table_list_by_llm_guess_str = self.globals.general_llm_adapter.process(select_tables_by_llm_guess_prompt)
        table_list_by_llm_guess = decode_llm_output_in_json_list_format(table_list_by_llm_guess_str)

        relevant_table_list = []
        for table_name in table_list_from_referenced_sql:
            if table_name not in relevant_table_list:
                relevant_table_list.append(table_name)

        for table_name in table_list_by_llm_guess:
            if table_name not in relevant_table_list:
                relevant_table_list.append(table_name)

        def remove_duplicates(list1, list2):
            # 将第一个列表转换为集合
            set1 = set(list1)
            # 使用列表推导式生成新的列表，去除重复元素
            result = [item for item in list2 if item not in set1]
            return result

        # select_table_from_referenced_sql_llm_transaction = LlmTransaction()
        # select_table_by_llm_guess_llm_transaction = LlmTransaction()
        #
        # select_table_from_referenced_sql_llm_transaction.llm_input = select_tables_from_refecenced_sql_prompt
        # select_table_from_referenced_sql_llm_transaction.llm_output = str(table_list_from_referenced_sql)
        # select_table_from_referenced_sql_llm_transaction.type = LLM_TRANSACTION_TYPE.SELECT_TABLE_FROM_REFENCED_TABLE.value
        # select_table_from_referenced_sql_llm_transaction.message_id = message_id
        #
        # select_table_by_llm_guess_llm_transaction.llm_input = select_tables_by_llm_guess_prompt
        # select_table_by_llm_guess_llm_transaction.llm_output = str(table_list_by_llm_guess)
        # select_table_by_llm_guess_llm_transaction.type = LLM_TRANSACTION_TYPE.SELECT_TABLE_BY_LLM_GUESS.value
        # select_table_by_llm_guess_llm_transaction.message_id = message_id
        #
        # self.save_llm_transaction(select_table_from_referenced_sql_llm_transaction)
        # self.save_llm_transaction(select_table_by_llm_guess_llm_transaction)

        table_list_by_llm_guess = remove_duplicates(table_list_from_referenced_sql, table_list_by_llm_guess)
        logger.debug("get_relevant_tables suc, table_list_from_referenced_sql: %s, table_list_form_llm_guess:%s" % (table_list_from_referenced_sql, table_list_by_llm_guess))
        return table_list_from_referenced_sql, table_list_by_llm_guess

    def generte_table_description_batch(self, table_ddl_list: list):
        output_table_description = ""
        index = 0
        for table_ddl in table_ddl_list:
            table_description = self.generte_table_descriptioin(table_ddl)
            table_description = "[Relevant Table %d]" % index + table_description + "\n\n"
            output_table_description += table_description
            index += 1

        logger.debug("generte_table_descriptioin_batch suc")
        return output_table_description

    def process(self, message: Message):
        data_source: DataSource = self.get_data_source(self.agent_meta.user_id, message.data_source_id)
        if data_source is None:
            logger.error("process failed, relevant_data_source_list cnt is 0")
            return "", "", "", "", "", "", ""

        user_question_vector = self.globals.text_embedding.get(message.person_input)


        user_qa_template = self.get_user_qa_template(user_question_vector, data_source.id)
        user_domain_knowledge = self.get_full_domain_knowledge(data_source.id)
        user_table_descriptions = self.get_user_table_descriptions(user_question_vector, data_source.id)

        table_list_from_referenced_sql, table_list_from_llm_guess = self.get_relevant_tables(message.person_input,
                                                                                             data_source,
                                                                                             user_table_descriptions,
                                                                                             user_domain_knowledge,
                                                                                             user_qa_template,
                                                                                             message.id)

        relevant_table_column = data_source.get_table_column_batch(table_list_from_referenced_sql, "high")
        relevant_table_column += data_source.get_table_column_batch(table_list_from_llm_guess, "low")

        env_info = get_env_info()

        generate_sql_prompt = generate_sql_prompt_template.replace("{relevant_table_column}", str(relevant_table_column)).replace("{user_table_descriptions}", str(user_table_descriptions)).\
    replace("{user_domain_knowledge}", str(user_domain_knowledge)).replace("{referenced_sql_statements}", str(user_qa_template)).replace("{user_question}", message.person_input).\
            replace("{env_info}", env_info)

        sql_cmd = self.globals.general_llm_adapter.process(generate_sql_prompt)
        from magic_bi.plugin.sql_plugin import SqlPlugin
        sql_plugin = SqlPlugin()
        (ret, sql_output) = sql_plugin.run(sql_cmd, data_source.url)

        if message.with_humman_readable_output is True and sql_output.strip() != "":
            prompt_answer_user = build_prompt_make_sql_output_human_readable(message.person_input, sql_output)
            human_readable_output = self.globals.general_llm_adapter.process(prompt_answer_user)
        else:
            human_readable_output = ""

        # generate_sql_llm_transaction = LlmTransaction()
        # generate_sql_llm_transaction.llm_input = generate_sql_prompt
        # generate_sql_llm_transaction.llm_output = sql_cmd
        # generate_sql_llm_transaction.type = LLM_TRANSACTION_TYPE.GENERATE_SQL.value
        # generate_sql_llm_transaction.message_id = message.id
        #
        # self.save_llm_transaction(generate_sql_llm_transaction)

        logger.debug("process suc")
        relevant_table_list = table_list_from_referenced_sql + table_list_from_llm_guess
        return sql_output, human_readable_output, sql_cmd, relevant_table_list, user_table_descriptions, \
            user_qa_template, user_domain_knowledge

    # def save_llm_transaction(self, transaction: LlmTransaction):
    #     with Session(GLOBALS.sql_orm.engine, expire_on_commit=False) as session:
    #         session.add(transaction)
    #         session.commit()

    def get_user_qa_template(self, user_question_vector: List, data_source_id: str) -> str:
        few_shot_examples = ""
        collection_id = get_qa_template_embedding_collection_id(data_source_id)
        result_list = self.globals.qdrant_adapter.search(collection_id, user_question_vector, cnt=2)

        index = 0
        for result in result_list:
            question = result.payload.get("question", "")
            answer = result.payload.get("answer", "")
            few_shot_example = f"question{index}:\n{question}\nanswer{index}:\n{answer}\n\n"
            few_shot_examples += few_shot_example
            index += 1

        if len(few_shot_examples) == 0:
            logger.error("get_few_shot_examples failed")
        else:
            logger.debug("get_few_shot_examplesv failed")

        return few_shot_examples

    def get_user_table_descriptions(self, user_question_vector: List, data_source_id: str) -> str:
        # table_name_collection_id = get_table_name_template_embedding_collection_id(data_source_id)
        collection_id = get_table_description_embedding_collection_id(data_source_id)
        result_list = self.globals.qdrant_adapter.search(collection_id, user_question_vector, cnt=10)

        table_descriptions = ""
        index = 0
        for result in result_list:
            table_name = result.payload.get("table_name", "")
            table_description = result.payload.get("table_description", "")
            table_description_item = f"{table_name}: {table_description}\n"
            table_descriptions += table_description_item
            index += 1

        if len(table_descriptions) == 0:
            logger.error("get_table_descriptions failed")
        else:
            logger.debug("get_table_descriptions suc")

        return table_descriptions


    # def get_table_column_descriptions(self):
    #     pass

    def get_relevant_domain_knowledge(self, user_question_vector: List, data_source_id: str) -> str:
        collection_id = get_domain_knowledge_embedding_collection_id(data_source_id)
        result_list = self.globals.qdrant_adapter.search(collection_id, user_question_vector, cnt=10, score_threshold=0.0)
        # result_list = self.globals.qdrant_adapter.get_points(collection_id)

        domain_knowledge = ""
        index = 0
        for result in result_list:
            knowledge = result.payload.get("content", "")
            domain_knowledge_item = f"knowledge{index}:\n{knowledge}\n\n"
            domain_knowledge += domain_knowledge_item
            index += 1

        if domain_knowledge == "":
            logger.error("get_domain_knowledge failed")
        else:
            logger.debug("get_domain_knowledge suc")

        return domain_knowledge

    def get_full_domain_knowledge(self, data_source_id: str) -> str:
        # domain_knowledge_list = []
        domain_knowledge = ""
        from magic_bi.data.data_source_knowledge.domain_knowledge import DomainKnowledge
        try:
            with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
                results = session.query(DomainKnowledge).filter(DomainKnowledge.data_source_id == data_source_id).all()

                index = 0
                for result in results:
                    knowledge = result.content
                    domain_knowledge_item = f"knowledge{index}:\n{knowledge}\n\n"
                    domain_knowledge += domain_knowledge_item
                    index += 1

        except Exception as e:
            logger.error("catch exception:%s" % str(e))

        logger.debug("get_full_domain_knowledge suc")
        return domain_knowledge

    def get_data_source(self, user_id: str, data_source_id: str) -> DataSource:
        with Session(self.globals.sql_orm.engine) as session:
            data_source_list: List[DataSource] = session.query(DataSource).filter(DataSource.id == data_source_id).all()

            if len(data_source_list) == 0:
                logger.error("get_data_source failed, user_id:%s, data_source_id:%s" % (user_id, data_source_id))
                return None

            data_source: DataSource = data_source_list[0]
            # data_source.generate_db_ddl()

            return data_source
