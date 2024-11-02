import time

import uuid
from sqlalchemy import Column, String, BigInteger, Integer, TEXT

from magic_bi.db.sql_orm import BASE


class TrainDataPromptedItem(BASE):
    __tablename__ = "train_data_prompted_item"
    id = Column(String, nullable=False)
    train_data_id = Column(String, nullable=False, primary_key=True)

    instruction = Column(String, primary_key=True)
    input = Column(String, primary_key=True)
    output = Column(String)

    generate_method = Column(String, nullable=False)
    add_timestamp = Column(BigInteger, nullable=False)

    def __init__(self):
        self.id = uuid.uuid1().hex
        self.train_data_id = ""

        self.instruction = ""
        self.input = ""
        self.output = ""

        self.generate_method = ""
        self.add_timestamp = int(time.time() * 1000)


    def from_dict(self, data_dict: dict):
        for key, value in data_dict.items():
            if key in self.__dict__ and value is not None:
                self.__dict__[key] = value

    def to_dict(self) -> dict:
        output_dict = {}
        output_dict["id"] = self.id
        output_dict["train_data_id"] = self.train_data_id

        output_dict["instruction"] = self.instruction
        output_dict["input"] = self.input
        output_dict["output"] = self.output

        output_dict["generate_method"] = self.generate_method
        output_dict["add_timestamp"] = self.add_timestamp

        return output_dict
