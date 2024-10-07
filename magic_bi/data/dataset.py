import time
import uuid
from typing import Dict, List
from sqlalchemy import Column, String, BigInteger, Integer

from magic_bi.db.sql_orm import BASE


# class DATA_TYPE(Enum):
#     TEXT = "text"
#     DOC = "doc"


class Dataset(BASE):
    __tablename__ = "dataset"
    id = Column(String, nullable=False)
    user_id = Column(String, nullable=False, primary_key=True)
    name = Column(String, primary_key=True)
    add_timestamp = Column(BigInteger, nullable=False)

    def __init__(self):
        self.id = uuid.uuid1().hex
        self.user_id = ""
        self.name = ""
        self.add_timestamp = int(time.time() * 1000)

    def from_dict(self, data_dict: Dict):
        for key, value in data_dict.items():
            if key in self.__dict__ and value is not None:
                self.__dict__[key] = value

    def to_dict(self) -> Dict:
        output_dict = {}
        output_dict["id"] = self.id
        output_dict["user_id"] = self.user_id
        output_dict["name"] = self.name
        output_dict["add_timestamp"] = self.add_timestamp

        return output_dict
