import os
import time

import uuid
from enum import Enum
from sqlalchemy import Column, String, BigInteger, Integer, TEXT

from magic_bi.db.sql_orm import BASE
from fastapi import UploadFile
from magic_bi.utils.utils import get_bytes_hash

class DOMAIN_MODEL_STATE(Enum):
    NOT_TRAINED = "not_trained"
    TRAINING = 'training'
    TRAINED = 'trained'
    DEPLOYING = 'deploying'
    DEPLOYED = 'deployed'

class DomainModel(BASE):
    __tablename__ = "domain_model"
    id = Column(String, nullable=False)
    user_id = Column(String, nullable=False, primary_key=True)
    name = Column(String, primary_key=True)
    size = Column(Integer)
    base_model = Column(String)
    state = Column(String)
    add_timestamp = Column(BigInteger, nullable=False)

    def __init__(self):
        self.id = uuid.uuid1().hex
        self.user_id = ""
        self.name = ""
        self.size = 0
        self.base_model = ""
        self.state = DOMAIN_MODEL_STATE.NOT_TRAINED.value
        self.add_timestamp = int(time.time() * 1000)

    def from_dict(self, data_dict: dict):
        for key, value in data_dict.items():
            if key in self.__dict__ and value is not None:
                self.__dict__[key] = value

    def to_dict(self) -> dict:
        output_dict = {}
        output_dict["id"] = self.id
        output_dict["user_id"] = self.user_id
        output_dict["name"] = self.name
        output_dict["size"] = self.size
        output_dict["base_model"] = self.base_model
        output_dict["state"] = self.state
        output_dict["add_timestamp"] = self.add_timestamp

        return output_dict
