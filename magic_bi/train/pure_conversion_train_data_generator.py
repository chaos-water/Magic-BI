import json

import pandas as pd

from magic_bi.data.data_source import DataSource
from magic_bi.agent.sql.finetuned_llm_sql_agent import select_tables_prompt_template, generate_sql_prompt_template
from magic_bi.utils.utils import get_env_info, decode_json_list_from_llm_output
from magic_bi.train.utils import update_train_data_original_item, update_train_data_prompted_item
from magic_bi.train.train_data_type import TRAIN_DATA_GENERATE_METHOD, TRAIN_DATA_ITEM_VALID_RESULT, TRAIN_DATA_GENERATE_STATE
from magic_bi.train.utils import get_previous_llm_process_index, get_train_data
from magic_bi.train.entity.train_data import TrainData

select_tables_from_referenced_sql_prompt_template = \
'''[Sql Statement]:
    {sql_statement}

Identify the tables from [Sql Statement] that you think may answer the user's question.
Output the table names in json list format directly without any explanation.'''


from loguru import logger


from magic_bi.utils.globals import Globals
class PureConversionTrainDataGenerator:
    def __init__(self):
        self.globals: Globals = None
        self.data_source: DataSource = None
        self.train_data_id: str = ""
        self.full_table_list = []

    def init(self, globals: Globals) -> int:
        self.globals = globals
        # self.data_source = data_source
        # self.train_data_id = train_data_id

        logger.debug("FewShotTrainDataGenerator init suc")
        return 0

    def start(self, user_id: str, train_qa_file_id: str, sheet_name: str, train_data_name: str, data_source_id, table_list: list) -> int:
        train_data: TrainData = TrainData()
        train_data.user_id = user_id
        train_data.train_qa_file_id = train_qa_file_id
        train_data.sheet_name = sheet_name
        train_data.name = train_data_name
        train_data.generate_method = TRAIN_DATA_GENERATE_METHOD.FEW_SHOT.value
        train_data.generate_state = TRAIN_DATA_GENERATE_STATE.GENERATING.value
        train_data.data_source_id = data_source_id
        train_data.table_list = table_list


        from sqlalchemy.orm.session import Session

        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            session.add(train_data)
            session.commit()

        return self.execute(train_data)

    def resume(self, train_data_id: str):
        from magic_bi.train.utils import get_train_data
        train_data: TrainData = get_train_data(train_data_id)
        return self.execute(train_data)

    def execute(self, train_data: TrainData):
        excel_file_bytes, ret = self.globals.oss_factory.get_file(train_data.train_qa_file_id)
        from magic_bi.train.utils import parse_excel_to_json
        user_question_and_sql_list = parse_excel_to_json(excel_file_bytes, sheet_name=train_data.sheet_name)

        if train_data.current_processed_index >= len(user_question_and_sql_list):
            logger.debug(f"execute suc, train_data {train_data.id} already reached {train_data.item_cnt}")
            return

        from magic_bi.train.utils import get_data_source
        self.data_source: DataSource = get_data_source(train_data.data_source_id)
        self.full_table_list = self.data_source.get_table_list()
        self.train_data_id = train_data.id

        current_cnt = train_data.current_processed_index

        user_question_enhance_cnt, quant_number_enhance_cnt = self.calculate_augment_cnt(train_data.to_reach_item_cnt, len(user_question_and_sql_list))
        for user_question_and_sql in user_question_and_sql_list[current_cnt:]:
            try:
                self.generate_train_data_item(user_question_and_sql[0], user_question_and_sql[1], user_question_enhance_cnt, \
                                              quant_number_enhance_cnt)
            except Exception as e:
                logger.error("catch exception:%s" % str(e))
                logger.error("FewShotTrainDataGenerator execute failed")

            current_cnt += 1

    def generate_train_data_item(self, user_question: str, sql_cmd: str):
        relevant_table_list: list = self.get_table_list_from_sql_cmd(sql_cmd)

        changed_user_question_list = [user_question]

        for changed_user_question in changed_user_question_list:
            update_train_data_original_item(self.train_data_id, changed_user_question, sql_cmd,
                                            TRAIN_DATA_GENERATE_METHOD.PURE_CONVERSION,
                                            TRAIN_DATA_ITEM_VALID_RESULT.VALID)
            update_train_data_prompted_item(self.train_data_id, changed_user_question, sql_cmd, relevant_table_list,
                                            self.full_table_list, self.data_source, TRAIN_DATA_GENERATE_METHOD.PURE_CONVERSION)

    def get_table_list_from_sql_cmd(self, sql_cmd: str) -> list:
        prompt = select_tables_from_referenced_sql_prompt_template.replace("{sql_statement}", sql_cmd)

        table_list_str = self.globals.general_llm_adapter.process(prompt)
        from magic_bi.utils.utils import decode_json_list_from_llm_output
        table_list = decode_json_list_from_llm_output(table_list_str)
        return table_list

    def generate_train_data(self, user_question: str, sql_cmd, full_table_list: list, train_data_list: list) -> int:
        env_info = get_env_info()
        table_list_from_sql = self.get_table_list_from_sql_cmd(sql_cmd)

        table_column = self.data_source.get_table_column_batch(full_table_list, is_mini=True)
        select_table_prompt = select_tables_prompt_template.replace("{user_question}", user_question).replace(
            "{table_descriptions}", table_column)

        relevant_table_description = self.data_source.get_table_column_batch(table_list_from_sql)
        generate_sql_prompt = generate_sql_prompt_template.replace("{env_info}", env_info). \
            replace("{relevant_table_descriptions}", relevant_table_description). \
            replace("{user_question}", user_question)

        select_table_output_item = {"input": ""}
        select_table_output_item["instruction"] = select_table_prompt
        select_table_output_item["output"] = json.dumps(table_list_from_sql)
        train_data_list.append(select_table_output_item)

        generate_sql_output_item = {"input": ""}
        generate_sql_output_item["instruction"] = generate_sql_prompt
        generate_sql_output_item["output"] = sql_cmd
        train_data_list.append(generate_sql_output_item)

        logger.debug(
            "instruction1 length:%d, instruction2 length:%d" % (len(select_table_prompt), len(generate_sql_prompt)))
        return max(len(select_table_prompt), len(generate_sql_prompt))

    def is_start_json_para_legal(json_para: dict) -> bool:
        try:
            if json_para["train_qa_file_id"] != "" and json_para["data_source_id"] != "" and json_para["train_data_name"] != "":
                return True

        except Exception as e:
            logger.error(f"json_para {json_para} is illegal")
            return False

    def is_resume_json_para_legal(json_para: dict) -> bool:
        try:
            if json_para["train_data_id"] != "":
                return True

        except Exception as e:
            logger.error(f"json_para {json_para} is illegal")
            return False

    def calculate_augment_cnt(self, to_reach_item_cnt, input_item_cnt) -> (int, int):
        quant_number_enhance_cnt = 1
        while True:
            user_question_enhance_cnt = 2 * quant_number_enhance_cnt
            product = input_item_cnt * quant_number_enhance_cnt * user_question_enhance_cnt
            if product >= to_reach_item_cnt:
                return quant_number_enhance_cnt, user_question_enhance_cnt
            quant_number_enhance_cnt += 1

        return user_question_enhance_cnt, quant_number_enhance_cnt