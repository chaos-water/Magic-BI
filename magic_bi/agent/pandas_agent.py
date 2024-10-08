from magic_bi.agent.memmory import Memmory
from sqlalchemy.orm import Session
import json
from loguru import logger
from typing import List

from magic_bi.agent.base_agent import BaseAgent
from magic_bi.message.message import Message
from magic_bi.agent.utils import get_relevant_data_source
from magic_bi.utils.globals import Globals
from magic_bi.io.base_io import BaseIo
from magic_bi.data.data_source import DataSource
from magic_bi.data.data import Data, DATA_TYPE
from magic_bi.agent.agent_meta import AgentMeta
from magic_bi.model.base_llm_adapter import BaseLlmAdapter
from magic_bi.utils.globals import GLOBALS
# from magic_bi.agent.pandas_agent.prompt import build_prompt_query_data, build_prompt_answer_user

'''
[CONTEXT OF THE PREVIOUS CONVERSATION]
{memmory}
'''
sqlalchemy_prompt_template_query_data = '''
[OPTIONAL DATA CONNECTORS]:
data_source_name | data_source_url ｜ table descriptions
-----------------------
{provided_data_sources}

[PERSON INPUT]:
{person_input}

[OUTPUT CODE EXAMPLE]:
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd

# 填写你的数据库连接信息
db_host = '127.0.0.1'
db_port = 5432
db_user = 'writer'
db_password = 'Abc123567.'
db_name = 'pandasai_db'  # 只考虑一个数据库

# 创建数据库引擎
db_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
engine = create_engine(db_url)

# 创建会话
Session = sessionmaker(bind=engine)
session = Session()

# 查询数据库中的数据
sql_query = "SELECT * FROM table1"

# 执行查询并将结果转化为 Pandas DataFrame
result = session.execute(sql_query)
df = pd.DataFrame(result.fetchall(), columns=result.keys())

# 打印 DataFrame
print(df.to_string())

# 关闭会话
session.close()


Output the python code if you find the appropriate databases and tables from the [OPTIONAL DATA CONNECTORS].

DO NOT NEED ANY EXPLANATION.
'''

"""
[CONTEXT OF THE PREVIOUS CONVERSATION]
{memmory}
"""
pandas_prompt_template_query_data = '''
[OPTIONAL DATA CONNECTORS]:
data_source_name | data_source_url ｜ table descriptions
-----------------------
{provided_data_sources}

[PERSON INPUT]:
{person_input}

[OUTPUT CODE EXAMPLE]:
import pandas as pd
import psycopg2  # 或者根据你使用的数据库类型选择合适的库

# 填写你的数据库连接信息
db_host = '127.0.0.1'
db_port = 5432
db_user = 'writer'
db_password = 'Abc123567.'
db_name1 = 'pandasai_db'
db_name2 = 'test_db'

# 连接数据库1（pandasai_db）
conn1 = psycopg2.connect(
    host=db_host,
    port=db_port,
    user=db_user,
    password=db_password,
    database=db_name1
)

# 连接数据库2（test_db）
conn2 = psycopg2.connect(
    host=db_host,
    port=db_port,
    user=db_user,
    password=db_password,
    database=db_name2
)

# 查询数据库1中的数据
sql_query1 = "SELECT * FROM table1"

# 查询数据库2中的数据
sql_query2 = "SELECT * FROM table2"

# 使用 pandas 读取数据
df1 = pd.read_sql_query(sql_query1, conn1)
df2 = pd.read_sql_query(sql_query2, conn2)

# 关闭连接
conn1.close()
conn2.close()

# 合并数据
merged_df = pd.merge(df1, df2, on='example_key', how='inner')  # 假设你要基于 user_id 进行合并

# 打印或者进一步处理数据
print(merged_df.to_string())

Output the python code if you find the appropriate databases and tables from the [OPTIONAL DATA CONNECTORS].

DO NOT NEED ANY EXPLANATION.
'''


def build_prompt_query_data(person_input: str, data_source_list: List[DataSource], memmory: str):
    provided_data_sources = ""
    for data_source in data_source_list:
        provided_data_sources += data_source.get_meta_info()

    return sqlalchemy_prompt_template_query_data.replace("{person_input}", person_input). \
        replace("{provided_data_sources}", provided_data_sources)
        # replace("{memmory}", memmory)


prompt_template_query_data_fix_error = '''
[OPTIONAL DATA CONNECTORS]:
data_source_name | data_source_url ｜ table descriptions
-----------------------
{provided_data_sources}

[PERSON INPUT]:
{person_input}

[PREVIOUS CODE]
{previous_code}

[PREVIOUS ERROR]:
{previous_error}

Based on the above, fix previous code error to accomplish to satisfy user requirements.
'''


def build_prompt_query_data_fix_error(person_input: str, data_source_list: List[DataSource], previous_code: str = "", previous_error: str = ""):
    provided_data_sources = ""
    for data_source in data_source_list:
        provided_data_sources += data_source.get_meta_info()

    return prompt_template_query_data_fix_error.replace("{person_input}", person_input). \
                                                replace("{provided_data_sources}", provided_data_sources). \
                                                replace("{person_input}", person_input). \
                                                replace("{previous_code}", previous_code). \
                                                replace("{previous_error}", previous_error)

def decode_llm_output_query_data(output: str) -> str:
    python_code = output
    from magic_bi.plugin.python_plugin import PythonPlugin

    python_plugin = PythonPlugin()
    plugin_output = python_plugin.run(python_code)

    logger.debug("decode_llm_output suc")
    return plugin_output


'''
[CONTEXT OF THE PREVIOUS CONVERSATION]
    {memmory}
'''
prompt_template_answer_user = '''
[USER INPUT]:
    {user_input}

[RETRIEVED DATA]:
    {retrieved_data}


If the RETRIEVED DATA is not blank. Answer the user input based on the retrieved data in Chinese. 
If the RETRIEVED DATA is blank. Refuse to answer the user politely in Chinese, and try to ask he or she to provide more detailed and accurate data.
'''

'''
# Based on the above, answer the user input based on the retrieved data in Chinese. 
'''


def build_prompt_answer_user(person_input: str, retrieved_data: str, memmory: str = ""):
    # prompt = prompt_template_answer_user.format(user_input=person_input, retrieved_data=retrieved_data, memmory=memmory)
    prompt = prompt_template_answer_user.format(user_input=person_input, retrieved_data=retrieved_data)
    return prompt


def decode_llm_output_answer_user(output: str) -> str:
    output = output.strip("'''").lstrip("python")
    return output

"""
[CONTEXT OF THE PREVIOUS CONVERSATION]
{memmory}
"""
def get_relevant_data_source(llm_adapter: BaseLlmAdapter, person_input: str, authorized_data_source_list: List, memmory: str):
    prompt_template_relevant_data_source = '''
[OPTIONAL DATA CONNECTORS]:
    data_source_name | data connector url | data connector meta info
    -----------------------
    {provided_data_sources}

[OUTPUT FORMAT]:
    {"data_source_name": "data_source_url"}

[EXAMPLE OUTPUT]:
    {"data_source_name1": "data_source_url1", "data_source_name2": "data_source_url2"}

[PERSON INPUT]:
    {person_input}

Based on the above, output the data_sources which are relevant with the person input. Just output the json format data, no other explanation.
'''

    def build_prompt_relevant_data_source(person_input: str, data_source_list: List[DataSource], memmory: str= ""):
        provided_data_sources = ""
        for data_source in data_source_list:
            provided_data_sources += data_source.get_meta_info()

        return prompt_template_relevant_data_source.replace("{person_input}", person_input). \
            replace("{provided_data_sources}", provided_data_sources)
            # replace("{provided_data_sources}", provided_data_sources).replace("{memmory}", memmory)

    def decode_llm_output_relevant_data_source(output: str, authorized_data_source_list: List) -> list[DataSource]:
        relevant_data_source_list = []
        try:
            relevant_data_source_dict = json.loads(output)
            for data_source in authorized_data_source_list:
                if data_source.name in relevant_data_source_dict:
                    relevant_data_source_list.append(data_source)

        except Exception as e:
            pass

        return relevant_data_source_list

    prompt = build_prompt_relevant_data_source(person_input, authorized_data_source_list, memmory)
    llm_output = llm_adapter.process(prompt)
    relevant_data_source_list = decode_llm_output_relevant_data_source(llm_output, authorized_data_source_list=authorized_data_source_list)

    logger.debug("get_relevant_data_source suc, relevant_data_source_list cnt:%d" % len(relevant_data_source_list))
    return relevant_data_source_list

'''
[CONTEXT OF THE PREVIOUS CONVERSATION]
    {memmory}
'''
def get_relevant_data(llm_adapter: BaseLlmAdapter, person_input: str, authorized_data_list: List, memmory: str):
    prompt_template_relevant_data = '''
[OPTIONAL DATA]:
    data_name | data meta info
    -----------------------
    {provided_data}

[OUTPUT FORMAT]:
    ["data_name"]

[EXAMPLE OUTPUT]:
    ["data_name1", "data_name2", "data_name3"]

[PERSON INPUT]:
    {person_input}

Based on the above, output the data which are relevant with the person input. Just output the json format data, no other explanation.
'''

    def generate_data_meta_info(data: Data) -> str:
        if data.type == DATA_TYPE.DOC.value:
            str_with_meta_info = "%s | \n" % (data.name)
        elif data.type == DATA_TYPE.SQL_DB.value:
            from sqlalchemy.orm.session import Session
            from typing import List

            with Session(GLOBALS.sql_orm.engine) as session:
                data_source_list: List[DataSource] = session.query(DataSource).filter(DataSource.id == data.hash).all()
                if len(data_source_list) == 0:
                    return ""

                data_source: DataSource = data_source_list[0]
                data_source.generate_meta_info()
                str_with_meta_info = "%s | %s\n" % (data.name, data_source.meta_info_list)
        else:
            pass

        return str_with_meta_info

    def build_prompt_relevant_data(person_input: str, data_list: List[Data]):
        provided_data = ""
        for data in data_list:
            provided_data += generate_data_meta_info(data)

        return prompt_template_relevant_data.replace("{person_input}", person_input). \
            replace("{provided_data}", provided_data)
            # replace("{provided_data}", provided_data).replace("memmory", memmory)

    def decode_llm_output_relevant_data(output: str, authorized_data_list: List) -> list[Data]:
        relevant_data_list = []
        try:
            relevant_data_dict = json.loads(output)
            for data in authorized_data_list:
                if data.name in relevant_data_dict:
                    relevant_data_list.append(data)

        except Exception as e:
            logger.error("catch exception:%s" % str(e))
            return relevant_data_list

        return relevant_data_list

    prompt = build_prompt_relevant_data(person_input, authorized_data_list)
    llm_output = llm_adapter.process(prompt)
    relevant_data_list = decode_llm_output_relevant_data(llm_output, authorized_data_list=authorized_data_list)

    logger.debug("get_relevant_data suc, relevant_data_list cnt:%d" % len(relevant_data_list))
    return relevant_data_list

class PandasAgent(BaseAgent):
    def __init__(self):
        self.memmory: Memmory = Memmory()
        super().__init__()

    def init(self, agent_meta: AgentMeta, globals: Globals, io: BaseIo) -> int:
        super().init(agent_meta, globals, io)
        self.memmory.init(globals=globals, agent_id=agent_meta.id, context_size=globals.general_llm_adapter.get_model_config().context_size)

        logger.debug("init suc")
        return 0

    def process(self, message: Message) -> str:
        assistant_output = ""
        if message.data_source_id != "":
            assistant_output = self.process_in_data_source_type(message)
        elif message.dataset_id != "":
            assistant_output = self.process_in_dataset_type(message)
        elif message.data_id != "":
            assistant_output = self.process_in_data_type(message)
        else:
            logger.error("process failed")
            return assistant_output

        message.assistant_output = assistant_output
        self.memmory.add_message(message)

        logger.debug("process suc")
        return assistant_output

    def process_in_data_source_type(self, message: Message) -> str:
        relevant_data_source = self.get_relevant_data_source_from_input(self.agent_meta.user_id,
                                                                              message.person_input,
                                                                              message.data_source_id)

        prompt_query_data = build_prompt_query_data(message.person_input, relevant_data_source, self.memmory.get_memory_str())
        llm_output_query_data = self.globals.general_llm_adapter.process(prompt_query_data)
        from magic_bi.plugin.python_plugin import PythonPlugin
        python_plugin: PythonPlugin = PythonPlugin()

        retry_cnt = 1
        while retry_cnt <= self.agent_meta.max_retry_cnt:
            ret, python_output, cleaned_python_code = python_plugin.run(llm_output_query_data)
            if ret == 0:
                break

            prompt_query_data_fix_error = build_prompt_query_data_fix_error(message.person_input, relevant_data_source, cleaned_python_code, python_output)
            llm_output_query_data = self.globals.general_llm_adapter.process(prompt_query_data_fix_error)

            retry_cnt += 1

        if retry_cnt > self.agent_meta.max_retry_cnt:
            pass

        prompt_answer_user = build_prompt_answer_user(message.person_input, python_output, self.memmory.get_memory_str())
        assistant_output = self.globals.general_llm_adapter.process(prompt_answer_user)

        logger.debug("process_in_data_source_type suc")
        return assistant_output

    def process_in_dataset_type(self, message: Message) -> str:
        relevant_data_source = self.get_relevant_data_from_input(self.agent_meta.user_id, message.person_input, message.dataset_id)
        # from magic_bi.agent.pandas_agent.prompt import build_prompt_query_data, build_prompt_answer_user
        prompt_query_data = build_prompt_query_data(message.person_input, relevant_data_source)
        llm_output_query_data = self.globals.general_llm_adapter.process(prompt_query_data)
        # cleaned_llm_output_query_data = self.try_to_clean_python_code(llm_output_query_data)
        from magic_bi.plugin.python_plugin import PythonPlugin
        python_plugin: PythonPlugin = PythonPlugin()
        python_output = python_plugin.run(llm_output_query_data)

        prompt_answer_user = build_prompt_answer_user(message.person_input, python_output)
        llm_output_answer_user = self.globals.general_llm_adapter.process(prompt_answer_user)
        assistant_output = llm_output_answer_user

        logger.debug("process_in_dataset_type suc")
        return assistant_output

    def process_in_data_type(self, message: Message) -> str:
        relevant_data_source = self.get_relevant_data_from_input(self.agent_meta.user_id, message.person_input, message.dataset_id)
        prompt_query_data = build_prompt_query_data(message.person_input, relevant_data_source)
        llm_output_query_data = self.globals.general_llm_adapter.process(prompt_query_data)
        # cleaned_llm_output_query_data = self.try_to_clean_python_code(llm_output_query_data)
        from magic_bi.plugin.python_plugin import PythonPlugin
        python_plugin: PythonPlugin = PythonPlugin()
        python_output = python_plugin.run(llm_output_query_data)

        prompt_answer_user = build_prompt_answer_user(message.person_input, python_output)
        llm_output_answer_user = self.globals.general_llm_adapter.process(prompt_answer_user)
        assistant_output = llm_output_answer_user

        logger.debug("process_in_data_type suc")
        return assistant_output

    def run(self) -> int:
        while True:
            message: Message = Message(self.agent_id)
            message.person_input = self.io.input()
            if message.person_input.strip(" ") == "":
                self.io.output(self.globals.tips.get_tips().USER_INPUT_IS_EMPTY.value)
                continue

            relevant_data_source = self.get_relevant_data_source_from_input("test_user", message.person_input)
            from magic_bi.agent.pandas_agent.prompt import build_prompt_query_data, build_prompt_answer_user
            prompt_query_data = build_prompt_query_data(message.person_input, relevant_data_source)
            llm_output_query_data = self.globals.general_llm_adapter.process(prompt_query_data)

            prompt_answer_user = build_prompt_answer_user(message.person_input, llm_output_query_data)
            llm_output_answer_user = self.globals.general_llm_adapter.process(prompt_answer_user)
            message.assistant_output = llm_output_answer_user
            self.io.output(message.assistant_output)

    def get_relevant_data_source_from_input(self, user_id: str, person_input: str, data_source_id: str) -> list[DataSource]:
        if data_source_id != "all":
            with Session(self.globals.sql_orm.engine) as session:
                relevant_data_source_list: List[DataSource] = session.query(DataSource).filter(DataSource.id == data_source_id).all()

        else:
            with Session(self.globals.sql_orm.engine) as session:
                authorized_data_source_list: List[DataSource] = session.query(DataSource).filter(DataSource.user_id == user_id).all()

            for authorized_data_source in authorized_data_source_list:
                authorized_data_source.generate_meta_info()

            relevant_data_source_list: str = get_relevant_data_source(self.globals.general_llm_adapter, person_input,
                                                                            authorized_data_source_list,
                                                                            self.memmory.get_memory_str())

        for relevant_data_source in relevant_data_source_list:
            relevant_data_source.generate_meta_info()

        logger.debug("get_relevant_data_source_from_input suc")
        return relevant_data_source_list

    def get_relevant_data_from_input(self, user_id: str, person_input: str, dataset_id: str, memmory: str) -> list[DataSource]:
        with Session(self.globals.sql_orm.engine) as session:
            authorized_data_list: List[Data] = session.query(Data).filter(Data.dataset_id == dataset_id, Data.user_id == user_id).all()

        # for authorized_data in authorized_data_list:
        #     authorized_data.generate_meta_info()

        relevant_data_list: str = get_relevant_data(self.globals.general_llm_adapter, person_input, authorized_data_list, memmory)
        for relevant_data in relevant_data_list:
            relevant_data.generate_meta_info()

        logger.debug("get_relevant_data_from_input suc")
        return relevant_data_list