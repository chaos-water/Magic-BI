import time
from loguru import logger
import uuid
from enum import Enum
from sqlalchemy import Column, String, BigInteger, Integer, create_engine, inspect, Text, select
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

from magic_bi.db.sql_orm import BASE
from magic_bi.utils.utils import format_db_url


def get_qa_template_embedding_collection_id(data_source_id: str):
    return data_source_id + "_qa_template"

def get_table_description_embedding_collection_id(data_source_id: str):
    return data_source_id + "_table_description"

def get_domain_knowledge_embedding_collection_id(data_source_id: str):
    return data_source_id + "_domain_knowledge"

class DATA_SOURCE_TYPE(Enum):
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"

class DataSourceOrm(BASE):

    __tablename__ = "data_source"
    id = Column(String, nullable=False)
    user_id = Column(String, nullable=False, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    url = Column(String, nullable=False, primary_key=True)
    add_timestamp = Column(BigInteger, nullable=False)

    def __init__(self):
        self.id = uuid.uuid1().hex
        self.add_timestamp = int(time.time() * 1000)
        self.user_id = ""
        self.type = ""
        self.name = ""
        self.url = ""

    def from_dict(self, data_dict: dict):
        for key, value in data_dict.items():
            if key in self.__dict__ and value is not None:
                self.__dict__[key] = value

    def to_dict(self) -> dict:
        return self.__dict__

# 为这部分代码添加个功能，输入一个表名table_name和一个大于零的整数cnt，返回一个字符串。这个字符串的第一行是表名，后续的几行是表中的cnt条数据值。
# 字符串打印出来的效果，类似数据库软件中呈现的效果，有较好的可视化效果。

class DataSource():
    def __init__(self):
        self.orm = None
        self.engine = None
        self.session = None

    def __exit__(self):
        if self.session is not None:
            self.session.close()
        if self.engine is not None:
            self.engine.dispose()

    def init(self, data_source_orm: DataSourceOrm) -> int:
        self.orm = data_source_orm
        data_source_url = format_db_url(self.orm.url)
        try:
            self.engine = create_engine(data_source_url)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            self.engine.connect()

            logger.debug("DataSource init suc")
            return 0
        except Exception as e:
            logger.error("DataSource init failed")
            return -1

    def get_table_column_batch(self, table_list: list, priority: str="", is_mini: bool = False):
        full_table_description = ""
        index = 0
        for table in table_list:
            if is_mini:
                table_description = self.get_table_column_mini_v3(table, index)
            else:
                table_description = self.get_table_column(table, index, priority, with_index=True, with_column_type=True, \
                                                          with_primary_key=True)
            full_table_description += table_description
            index += 1

        logger.debug("get_table_description_batch suc")
        return full_table_description

    def get_table_column(self, table_name, table_index: int, priority: str="", with_index: bool=False, \
                         with_column_type: bool=False, with_primary_key: bool=False):
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=self.engine)

        columns = []
        for column in table.columns:
            column_name = column.name
            column_type = str(column.type).replace(' COLLATE "utf8mb4_unicode_ci"', "")
            column_comment = column.comment if column.comment else ''
            columns.append({
                'column_name': column_name,
                'column_type': column_type,
                'column_comment': column_comment
            })

        primary_keys = {key.name for key in table.primary_key.columns}

        output = []
        output.append(f"\tTable: {table_name}")
        if priority != "":
            output.append(f"\tPriority: {priority}")

        if with_primary_key:
            primary_key_name = " | Primary Key"
        else:
            primary_key_name = ""

        if with_column_type:
            column_type_name = " | Column Type"
        else:
            column_type_name = ""

        column_title = "\tColumn Name%s | Column Comment%s" % (column_type_name, primary_key_name)
        output.append("")
        output.append(column_title)

        for column in columns:
            column_name = column['column_name']
            column_type = column['column_type']
            column_comment = column['column_comment'].strip("\n")
            pk_indicator = "PK" if column_name in primary_keys else ""
            if column_name.strip() == "":
                continue

            if with_column_type is True:
                column_type_name = f" | {column_type:<12}"
            else:
                column_type_name = ""

            if with_primary_key is True:
                primary_key_name = f" | {pk_indicator}"
            else:
                primary_key_name = ""

            output.append(f"\t{column_name:<15}{column_type_name} | {column_comment:<20}{primary_key_name}")

        if with_index is True:
            indexes = []
            for index in table.indexes:
                for column in index.columns:
                    indexes.append({
                        'index_name': index.name,
                        'column_name': column.name
                    })

            index_dict = {}
            for index in indexes:
                index_name = index['index_name']
                column_name = index['column_name']
                if index_name not in index_dict:
                    index_dict[index_name] = []
                index_dict[index_name].append(column_name)

            if len(index_dict) > 0:
                output.append("")
                output.append("\tIndexes:")
                output.append("\t" + "-" * 50)

                output.append("\tIndex | Column")
                for index_name, columns in index_dict.items():
                    output.append("\t" + f"{index_name} | {columns[0]}")

        if table_index == 0:
            output_str = "[Relevant Table Description %d]" % table_index + "\n"
        else:
            output_str = "\n\n[Relevant Table Description %d]" % table_index + "\n"

        output_str += "\n".join(output)

        return output_str

    def get_table_column_mini_v3(self, table_name, table_index: int):
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=self.engine)

        columns = []
        for column in table.columns:
            column_name = column.name
            column_type = str(column.type).replace(' COLLATE "utf8mb4_unicode_ci"', "")
            column_comment = column.comment if column.comment else ''
            columns.append({
                'column_name': column_name,
                'column_type': column_type,
                'column_comment': column_comment
            })

        output = []
        output.append(f"\tTable Name: {table_name}")

        column_title = "\tColumn Name | Column Comment"
        output.append(column_title)

        for column in columns:
            column_name = column['column_name']
            column_comment = column['column_comment'].strip("\n")
            if column_name.strip() == "":
                continue

            output.append(f"\t{column_name:<15} | {column_comment:<20}")

        if table_index == 0:
            output_str = "[Table %d]" % table_index + "\n"
        else:
            output_str = "\n\n[Table %d]" % table_index + "\n"

        output_str += "\n".join(output)

        return output_str

    def get_table_list(self) -> list[str]:
        inspector = inspect(self.engine)

        table_list = inspector.get_table_names()
        logger.debug("get_table_list, table_list cnt:%d" % len(table_list))
        return table_list

    # 对这部分代码做个改造，返回的数据是这个表中随机的cnt条数据。如果表中的数据量，不足cnt个，则全部返回。

    def get_table_data_preview(self, table_name: str, cnt: int) -> str:
        """
            获取指定表的随机 cnt 条数据并格式化成字符串显示。

            Args:
                table_name (str): 表名
                cnt (int): 要显示的行数

            Returns:
                str: 表名和随机 cnt 条数据的字符串
            """
        # 检查输入参数
        if cnt <= 0:
            raise ValueError("参数 cnt 必须是一个大于零的整数。")

        # 加载表
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=self.engine)

        # 查询表中所有数据的行数
        total_count = self.session.execute(select(func.count()).select_from(table)).scalar()

        # 如果数据量不足 cnt，则只查询全部数据；否则随机取 cnt 条
        limit = min(cnt, total_count)
        query = select(table).order_by(func.random()).limit(limit)
        result = self.session.execute(query).fetchall()

        return self.to_data_preview(table, table_name, result)
        # # 获取列名
        # column_names = [column.name for column in table.columns]
        #
        # # 格式化输出
        # output = [f"[Table {table_name} Data Preview]:", "-" * (len(table_name) + 7)]
        # header = " | ".join(column_names)
        # output.append(header)
        # output.append("-" * len(header))
        #
        # # 添加数据行
        # for row in result:
        #     row_data = " | ".join([str(value) for value in row])
        #     output.append(row_data)
        #
        # # 将输出转换成字符串
        # return "\n".join(output)

    def to_data_preview(self, table, table_name, result) -> str:
        import re

        # 获取列名
        column_names = [column.name for column in table.columns]

        # 格式化输出
        output = [f"[Table {table_name} Data Preview]:", "-" * (len(table_name) + 7)]
        header = " | ".join(column_names)
        output.append(header)
        output.append("-" * len(header))

        # 添加数据行
        for row in result:
            row_data = " | ".join([str(value) for value in row])
            output.append(row_data)

        # 将输出转换成字符串
        data_preview =  "\n".join(output)
        data_preview = re.sub(r'\n+', '\n', data_preview)
        return data_preview

    def get_table_data_preview_by_index(self, table_name: str, index: int, cnt: int=1) -> str:
        """
        获取指定表的第 index 行数据，如果 index 超过总行数，则返回最后一行数据。

        Args:
            table_name (str): 表名
            index (int): 要查询的行数索引（从0开始）

        Returns:
            str: 表的第 index 行数据或最后一行数据的字符串
        """
        # 加载表
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=self.engine)

        # 查询表中所有数据的行数
        total_count = self.session.execute(select(func.count()).select_from(table)).scalar()

        # 检查 index 是否超过总行数，若超过则设为最后一行的 index
        valid_index = min(index, total_count - 1)

        # 查询第 valid_index 行的数据
        query = select(table).offset(valid_index).limit(cnt)
        result = self.session.execute(query).fetchall()

        return self.to_data_preview(table, table_name, result)
        # 获取列名
        # column_names = [column.name for column in table.columns]
        #
        # # 格式化输出
        # output = [f"[Table {table_name} Row {valid_index}]:", "-" * (len(table_name) + 7)]
        # row_data = " | ".join(f"{col}: {val}" for col, val in zip(column_names, result))
        # output.append(row_data)
        #
        # # 将输出转换成字符串
        # return "\n".join(output)

    def to_str(self) -> str:
        return "%s | %s\n" % (self.name, self.url)
