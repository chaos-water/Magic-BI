from sqlalchemy.orm import Session
from loguru import logger

from magic_bi.config.system_config import SystemConfig
from magic_bi.agent.base_agent import BaseAgent
from magic_bi.message.message import Message
from magic_bi.utils.globals import Globals
from magic_bi.io.base_io import BaseIo
from magic_bi.data.data_source import DataSource, DataSourceOrm
from magic_bi.agent.agent_meta import AgentMeta
from magic_bi.utils.utils import get_env_info, decode_json_list_from_llm_output
from magic_bi.plugin.sql_plugin import SqlPlugin
from magic_bi.utils.error import ERROR_CODE, get_error_message
from magic_bi.prompt.finetuned_llm_sql_agent_prompt import *

def decode_llm_output_query_data(output: str) -> str:
    python_code = output
    from magic_bi.plugin.python_plugin import PythonPlugin

    python_plugin = PythonPlugin()
    plugin_output = python_plugin.run(python_code)

    logger.debug("decode_llm_output suc")
    return plugin_output


def build_prompt_make_sql_output_human_readable(person_input: str, retrieved_data: str, memmory: str = ""):
    prompt = prompt_template_make_sql_output_human_readable.format(user_input=person_input, retrieved_data=retrieved_data)
    return prompt

def decode_llm_output_answer_user(output: str) -> str:
    output = output.strip("'''").lstrip("python")
    return output

class FinetunedLlmSqlAgent(BaseAgent):
    def __init__(self):
        super().__init__()

    def init(self, agent_meta: AgentMeta, globals: Globals, io: BaseIo, system_config: SystemConfig) -> int:
        self.system_config = system_config
        super().init(agent_meta, globals, io, system_config)

        logger.debug("init suc")
        return 0

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
        try:
            sql_cmd = ""
            if self.system_config.memmory_enabled:
                exact_message: Message = self.memmory.try_get_exact_message(message)
                if exact_message is not None:
                    sql_cmd = exact_message.assistant_output

            data_source: DataSource = self.get_data_source(self.agent_meta.user_id, message.data_source_id)
            if sql_cmd == "":
                if data_source is None:
                    logger.error("process failed, relevant_data_source_list cnt is 0")
                    return ERROR_CODE.DATA_SOURCE_NOT_EXISTED.value, get_error_message(ERROR_CODE.DATA_SOURCE_NOT_EXISTED), "", "", ""

                full_table_list = data_source.get_table_list()
                table_descriptions = data_source.get_table_column_batch(full_table_list, is_mini=True)
                select_tables_prompt = select_tables_prompt_template.replace("{table_descriptions}", table_descriptions).\
                    replace("{user_question}", message.person_input)
                tables_list_str = self.globals.text2sql_llm_adapter.process(select_tables_prompt)
                relevant_table_list = decode_json_list_from_llm_output(tables_list_str)

                env_info = get_env_info()
                relevant_table_descriptions = data_source.get_table_column_batch(relevant_table_list)
                generate_sql_prompt = generate_sql_prompt_template.replace("{env_info}", env_info).\
                                                                    replace("{relevant_table_descriptions}", relevant_table_descriptions).\
                                                                    replace("{user_question}", message.person_input)
                sql_cmd = self.globals.text2sql_llm_adapter.process(generate_sql_prompt)

            sql_output = ""
            human_readable_output = ""
            if message.with_sql_result is True:
                sql_plugin = SqlPlugin()
                (ret, sql_output) = sql_plugin.run(sql_cmd, data_source.orm.url)

                if message.with_humman_readable_output is True and sql_output.strip() != "":
                    prompt_answer_user = build_prompt_make_sql_output_human_readable(message.person_input, sql_output)
                    human_readable_output = self.globals.general_llm_adapter.process(prompt_answer_user)

            message.assistant_output = sql_cmd
            if self.system_config.memmory_enabled:
                self.memmory.add_message(message)

            logger.debug("process suc")
            return ERROR_CODE.SUC.value, get_error_message(ERROR_CODE.SUC), sql_output, human_readable_output, sql_cmd

        except Exception as e:
            logger.error("catch exception:%s" % str(e))
            return ERROR_CODE.UNKNOWN_ERROR.value, get_error_message(ERROR_CODE.UNKNOWN_ERROR), "", "", ""

    def get_data_source(self, user_id: str, data_source_id: str) -> DataSource:
        with Session(self.globals.sql_orm.engine) as session:
            data_source_orm_list: list[DataSourceOrm] = session.query(DataSourceOrm).filter(DataSourceOrm.id == data_source_id).all()

            if len(data_source_orm_list) == 0:
                logger.error("get_data_source failed, user_id:%s, data_source_id:%s" % (user_id, data_source_id))
                return None

            data_source: DataSource = DataSource()
            data_source.init(data_source_orm_list[0])
            return data_source
