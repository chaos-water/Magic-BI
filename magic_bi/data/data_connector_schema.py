import time

import uuid
from enum import Enum
from typing import Dict
from sqlalchemy import Column, String, BigInteger, Integer, Text

# from magic_bi.data.data_connector import DataConnector
from magic_bi.db.sql_orm import BASE
from fastapi import UploadFile
from magic_bi.utils.utils import get_bytes_hash

class DATA_TYPE(Enum):
    SQL_DB = "sql_db"
    TEXT = "text"
    DOC = "doc"


class DataConnectorSchema(BASE):
    __tablename__ = "data_connector_schema"
    data_connector_id = Column(String, nullable=False)
    schema = Column(Text, nullable=False)
    add_timestamp = Column(BigInteger, nullable=False)

    def __init__(self):
        self.id = uuid.uuid1().hex
        self.add_timestamp = int(time.time() * 1000)
        self.file_bytes: bytes = None
        self.dataset_id: str = ""

    def from_dict(self, data_dict: Dict):
        for key, value in data_dict.items():
            if key in self.__dict__ and value is not None:
                self.__dict__[key] = value
        # self.dataset_id = data_dict.get("dataset_id", "")
        # self.user_id = data_dict.get("user_id", "")
        # self.name = data_dict.get("name", "")
        # self.hash = data_dict.get("hash", "")
        # self.type = data_dict.get("type", "")
        # if "id" in data_dict:
        #     self.id = data_dict.get("id", "")

    def to_dict(self) -> Dict:
        output_dict = {}
        output_dict["id"] = self.id
        output_dict["dataset_id"] = self.dataset_id
        output_dict["user_id"] = self.user_id
        output_dict["name"] = self.name
        output_dict["hash"] = self.hash
        output_dict["type"] = self.type
        output_dict["size"] = self.size
        output_dict["add_timestamp"] = self.add_timestamp

        return output_dict

    async def from_upload_file(self, upload_file: UploadFile):
        # self.file_bytes = syn_execute_asyn_func(upload_file.read())
        self.file_bytes = await upload_file.read()
        self.type = DATA_TYPE.DOC.value
        self.size = upload_file.size
        self.name = upload_file.filename
        self.hash = get_bytes_hash(self.file_bytes)

    # def to_str_with_meta_info(self) -> str:
        str_with_meta_info = ""
        # if self.type == DATA_TYPE.DOC.value:
        #     str_with_meta_info = "%s | \n" % (self.name)
        # elif self.type == DATA_TYPE.SQL_DB.value:
        #     # data_connector: DataConnector = DataConnector()
        #     from sqlalchemy.orm.session import Session
        #     from typing import List
        #     with Session(self.globals.sql_orm.engine) as session:
        #         data_connector_list: List[DataConnector] = session.query(DataConnector).filter(DataConnector.id == self.hash).all()
        #         if len(data_connector_list) > 0:
        #             return ""
        #
        #         data_connector: DataConnector = data_connector_list[0]
        #         data_connector.generate_meta_info()
        #         str_with_meta_info = "%s | %s\n" % (self.name, data_connector.meta_info_list)

        # else:
        #     pass
    #
    #     return str_with_meta_info
