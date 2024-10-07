import json
import uuid
from sqlalchemy import Column, String, BigInteger
from loguru import logger
import time

from typing import Dict
from magic_bi.db.sql_orm import BASE


class AppApi(BASE):
    __tablename__ = "app_api"
    user_id = Column(String, primary_key=True, nullable=False)
    app_id = Column(String, primary_key=True, nullable=False)
    path = Column(String, primary_key=True, nullable=False)
    method = Column(String, nullable=False)
    request_body = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    description = Column(String, nullable=False)
    parameters = Column(String, nullable=False)
    responses = Column(String, nullable=False)
    id = Column(String, nullable=False)
    add_timestamp = Column(BigInteger, nullable=False)

    def __init__(self):
        self.user_id = ""
        self.app_id = ""
        self.path = ""
        self.method = ""
        self.summary = ""
        self.description = ""
        self.parameters = ""
        self.responses = ""
        self.request_body = ""
        self.id = uuid.uuid1().hex
        self.add_timestamp = int(time.time() * 1000)

    def from_dict(self, input_dict: Dict) -> int:
        for key, value in input_dict.items():
            if key in self.__dict__ and value is not None:
                if isinstance(value, dict) or isinstance(value, list):
                    self.__dict__[key] =  json.dumps(value)
                else:
                    self.__dict__[key] = value

        logger.debug("from_dict suc")
        return 0

    def to_dict(self) -> Dict:
        output_dict = {}
        for key, value in self.__dict__.items():
            if key.startswith("_"):
                continue
            output_dict[key] = value

        return output_dict
