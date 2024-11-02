import json
from loguru import logger
from sqlalchemy.orm.session import Session

from magic_bi.train.entity.train_data_original_item import TrainDataOriginalItem
from magic_bi.train.train_data_type import TRAIN_DATA_GENERATE_METHOD
from magic_bi.utils.globals import GLOBALS
from magic_bi.train.entity.train_data_prompted_item import TrainDataPromptedItem
from magic_bi.train.train_data_type import TRAIN_DATA_ITEM_VALID_RESULT
from magic_bi.prompt.finetuned_llm_sql_agent_prompt import select_tables_prompt_template, generate_sql_prompt_template
from magic_bi.utils.utils import get_env_info
from magic_bi.train.entity.train_data import TrainData
from magic_bi.data.data_source import DataSourceOrm, DataSource

def update_train_data_original_item(train_data_id: str, user_question: str, sql_statement: str,
                                    generate_method: TRAIN_DATA_GENERATE_METHOD, valid_state: TRAIN_DATA_ITEM_VALID_RESULT):
    train_data_original_item: TrainDataOriginalItem = TrainDataOriginalItem()
    train_data_original_item.train_data_id = train_data_id
    train_data_original_item.input = user_question
    train_data_original_item.output = sql_statement
    train_data_original_item.generate_method = generate_method.value
    train_data_original_item.valid_result = valid_state.value

    try:
        with Session(GLOBALS.sql_orm.engine, expire_on_commit=False) as session:
            session.add(train_data_original_item)
            session.commit()
            logger.debug("update_train_data_item suc")
            return 0

    except Exception as e:
        logger.error("catch exception:%s" % str(e))
        logger.error("update_train_data_item failed")
        return -1

def update_train_data_prompted_item(train_data_id: str, user_question: str, sql_statement: str, relevant_table_list: list,
                                    full_table_list: list, data_source: DataSource, generate_method: TRAIN_DATA_GENERATE_METHOD):

    # full_table_list = data_source.get_table_list()
    full_table_descriptions = data_source.get_table_column_batch(full_table_list, is_mini=True)
    select_table_prompt = select_tables_prompt_template.replace("{user_question}", user_question).replace("{table_descriptions}", full_table_descriptions)
    env_info = get_env_info()
    relevant_table_descriptions = data_source.get_table_column_batch(relevant_table_list)
    generate_sql_prompt = generate_sql_prompt_template.replace("{env_info}", env_info).\
        replace("{relevant_table_descriptions}", relevant_table_descriptions). \
        replace("{user_question}", user_question)


    select_table_train_data_prompted_item: TrainDataPromptedItem = TrainDataPromptedItem()
    select_table_train_data_prompted_item.train_data_id = train_data_id
    select_table_train_data_prompted_item.instruction = select_table_prompt
    select_table_train_data_prompted_item.input = ""
    select_table_train_data_prompted_item.output = json.dumps(relevant_table_list)
    select_table_train_data_prompted_item.generate_method = generate_method.value

    generate_sql_train_data_prompted_item: TrainDataPromptedItem = TrainDataPromptedItem()
    generate_sql_train_data_prompted_item.train_data_id = train_data_id
    generate_sql_train_data_prompted_item.instruction = generate_sql_prompt
    generate_sql_train_data_prompted_item.input = ""
    generate_sql_train_data_prompted_item.output = sql_statement
    generate_sql_train_data_prompted_item.generate_method = generate_method.value

    try:
        with Session(GLOBALS.sql_orm.engine, expire_on_commit=False) as session:
            session.add(select_table_train_data_prompted_item)
            session.add(generate_sql_train_data_prompted_item)
            session.commit()
            logger.debug("update_train_data_item suc")
            return 0

    except Exception as e:
        logger.error("catch exception:%s" % str(e))
        logger.error("update_train_data_item failed")
        return -1

def clean_sql(input_sql: str) -> str:
    import re
    # 替换换行符为空格
    no_newlines = input_sql.replace('\n', ' ')
    # 将多个空格转化为一个空格
    single_spaced = re.sub(r'\s+', ' ', no_newlines)
    return single_spaced

# 在下边代码中，如何获取excel文件中的sheet name
def parse_excel_to_json(excel_file_bytes: bytes, sheet_name="Sheet1") -> list:
    # 将字节数据转换为 BytesIO 对象
    output_list: list = []
    from io import BytesIO
    import pandas as pd

    excel_file = BytesIO(excel_file_bytes)

    # 读取Excel数据
    df = pd.read_excel(excel_file, sheet_name=sheet_name, usecols=[0, 1])

    # result_dict = {}
    for row in df.itertuples(index=False):
        user_question = row[0]
        sql_cmd = clean_sql(row[1])  # 这里假设 clean_sql 是你自己的函数
        # result_dict[row[0]] = sql_cmd
        output_list.append([user_question, sql_cmd])

    return output_list

def get_previous_llm_process_index(train_data_id: str) -> int:
    try:
        with Session(GLOBALS.sql_orm.engine, expire_on_commit=False) as session:
            train_data_original_item: TrainDataOriginalItem = session.query(TrainDataOriginalItem).filter(TrainDataOriginalItem.train_data_id == train_data_id).\
                order_by(TrainDataOriginalItem.llm_process_index.desc()).limit(1).one_or_none()
            if train_data_original_item is None:
                previous_llm_process_index = 0
            else:
                previous_llm_process_index = train_data_original_item.llm_process_index

            logger.debug(f"get_previous_llm_process_index suc, previous_llm_process_index: {previous_llm_process_index}")
            return previous_llm_process_index

    except Exception as e:
        logger.error("catch exception:%s" % str(e))
        logger.error("get_previous_llm_process_index failed")
        return 0

def get_train_data(train_data_id: str) -> TrainData:
    try:
        with Session(GLOBALS.sql_orm.engine, expire_on_commit=False) as session:
            train_data: TrainData = session.query(TrainData).filter(TrainData.id == train_data_id).one_or_none()

            logger.debug(f"get_train_data suc")
            return train_data
    except Exception as e:
        logger.error("catch exception:%s" % str(e))
        logger.error("get_train_data failed")
        return None


def get_data_source(data_source_id: str) -> DataSource:
    try:
        with Session(GLOBALS.sql_orm.engine, expire_on_commit=False) as session:
            data_source_orm: DataSourceOrm = session.query(DataSourceOrm).filter(DataSourceOrm.id == data_source_id).one_or_none()
            data_source: DataSource = DataSource()
            data_source.init(data_source_orm)

            logger.debug("get_data_source suc")
            return data_source
    except Exception as e:
        logger.error("catch exception:%s" % str(e))
        logger.error("get_data_source failed")
        return None

def get_train_data_prompted_item(train_data_id: str) -> list[TrainDataPromptedItem]:
    try:
        with Session(GLOBALS.sql_orm.engine, expire_on_commit=False) as session:
            train_data_prompted_item_list: list[TrainDataPromptedItem] = \
                session.query(TrainDataPromptedItem).filter(TrainDataPromptedItem.train_data_id == train_data_id).all()

            logger.debug("get_train_data_prompted_item suc")
            return train_data_prompted_item_list
    except Exception as e:
        logger.error("catch exception:%s" % str(e))
        logger.error("get_train_data_prompted_item failed")
        return []
