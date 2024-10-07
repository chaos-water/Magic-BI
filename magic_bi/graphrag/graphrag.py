import time

import uuid
from enum import Enum
from typing import Dict
from sqlalchemy import Column, String, BigInteger, Integer

from magic_bi.db.sql_orm import BASE
from fastapi import UploadFile
from magic_bi.utils.utils import get_bytes_hash

class DATA_TYPE(Enum):
    SQL_DB = "sql_db"
    TEXT = "text"
    DOC = "doc"


class GraphRag(BASE):
    __tablename__ = "graph_rag"
    graph_id = Column(String, nullable=False)
    name = Column(String, nullable=False, primary_key=True)
    user_id = Column(String, nullable=False, primary_key=True)
    schema = Column(String, nullable=False)
    add_timestamp = Column(BigInteger, nullable=False)


    def __init__(self):
        self.graph_id = uuid.uuid1().hex
        self.name: str = ""
        self.user_id: str = ""
        self.add_timestamp: str = int(time.time() * 1000)

    def from_dict(self, data_dict: Dict):
        for key, value in data_dict.items():
            if key in self.__dict__ and value is not None:
                self.__dict__[key] = value

