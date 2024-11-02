import time

import uuid
from enum import Enum

from sqlalchemy import Column, String, BigInteger, Integer, Text

from magic_bi.db.sql_orm import BASE
from fastapi import UploadFile
from magic_bi.utils.utils import get_bytes_hash

class DATA_TYPE(Enum):
    SQL_DB = "sql_db"
    TEXT = "text"
    DOC = "doc"


class DataSourceSchema(BASE):
    __tablename__ = "data_source_schema"
    data_source_id = Column(String, nullable=False)
    schema = Column(Text, nullable=False)
    add_timestamp = Column(BigInteger, nullable=False)

    def __init__(self):
        self.id = uuid.uuid1().hex
        self.add_timestamp = int(time.time() * 1000)
        self.file_bytes: bytes = None
        self.dataset_id: str = ""

    def from_dict(self, data_dict: dict):
        for key, value in data_dict.items():
            if key in self.__dict__ and value is not None:
                self.__dict__[key] = value

    def to_dict(self) -> dict:
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

