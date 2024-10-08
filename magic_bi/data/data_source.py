import time
from loguru import logger
import uuid
from enum import Enum
from typing import Dict, List
from sqlalchemy import Column, String, BigInteger, Integer, create_engine, inspect, Text
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker

from magic_bi.db.sql_orm import BASE


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
    name = Column(String, nullable=False, primary_key=True)
    type = Column(String, nullable=False)
    url = Column(String, nullable=False)
    add_timestamp = Column(BigInteger, nullable=False)

    def __init__(self):
        self.id = uuid.uuid1().hex
        self.add_timestamp = int(time.time() * 1000)
        self.user_id = ""
        self.type = ""
        self.name = ""
        self.url = ""

    def from_dict(self, data_dict: Dict):
        for key, value in data_dict.items():
            if key in self.__dict__ and value is not None:
                self.__dict__[key] = value

    def to_dict(self) -> Dict:
        return self.__dict__

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
        self.engine = create_engine(self.orm.url)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        logger.debug("DataSource init suc")
        return 0

    def get_table_column_batch(self, table_list: List, priority: str="", is_mini: bool = False):
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


    def get_table_column_mini(self, table_name, table_index: int):
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=self.engine)

        # Get columns information
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

        columns_line = ""
        for column in columns:
            column_name = column['column_name']
            if column_name.strip() == "":
                continue

            columns_line += f"{column_name},"
        columns_line = columns_line.rstrip(",")
        output.append(f"{table_name}: {columns_line}\n\n")

        output_str = "\n".join(output)

        return output_str

    def get_table_column_mini_v2(self, table_name, table_index: int):
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
        output.append(f"\tTable: {table_name}")

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

    def get_table_list(self) -> List[str]:
        inspector = inspect(self.engine)

        table_list = inspector.get_table_names()
        logger.debug("get_table_list, table_list cnt:%d" % len(table_list))
        return table_list

    def to_str(self) -> str:
        return "%s | %s\n" % (self.name, self.url)

    # def from_dict(self, data_dict: Dict):
    #     for key, value in data_dict.items():
    #         if key in self.__dict__ and value is not None:
    #             self.__dict__[key] = value

    # def to_dict(self) -> Dict:
    #     return self.__dict__
