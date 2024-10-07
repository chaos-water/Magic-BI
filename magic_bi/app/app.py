import uuid
from sqlalchemy import Column, String, BigInteger
from loguru import logger
import time

from typing import Dict
from magic_bi.db.sql_orm import BASE


class App(BASE):
    __tablename__ = "app"
    user_id = Column(String, primary_key=True, nullable=False)
    name = Column(String, primary_key=True, nullable=False)
    host = Column(String, nullable=False)
    id = Column(String, nullable=False)
    add_timestamp = Column(BigInteger, nullable=False)

    def __init__(self):
        self.user_id = ""
        self.name = ""
        self.host = ""
        self.id = uuid.uuid1().hex
        self.add_timestamp = int(time.time() * 1000)

    def from_dict(self, input_dict: Dict) -> int:
        for key, value in input_dict.items():
            if key in self.__dict__ and value is not None:
                self.__dict__[key] =  value

        logger.debug("from_dict suc")
        return 0

    def to_dict(self) -> Dict:
        output_dict = {}
        for key, value in self.__dict__.items():
            if key.startswith("_"):
                continue
            output_dict[key] = value

        return output_dict
