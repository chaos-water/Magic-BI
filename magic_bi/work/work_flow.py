import uuid
import time
from sqlalchemy import Column, String, BigInteger, Integer, TEXT

from magic_bi.db.sql_orm import BASE

class WorkOfFlow(BASE):
    __tablename__ = "work_of_flow"
    work_flow_id = Column(String, nullable=False, primary_key=True)
    work_serial_number = Column(Integer, primary_key=True)
    work_name = Column(String, nullable=False)
    add_timestamp = Column(BigInteger, nullable=False)

    def __init__(self):
        self.work_flow_id = uuid.uuid4().hex
        self.work_serial_number = ""
        self.work_name = ""
        self.add_timestamp = 0


    def from_dict(self, data_dict: dict):
        for key, value in data_dict.items():
            if key in self.__dict__ and value is not None:
                self.__dict__[key] = value

    def to_dict(self) -> dict:
        output_dict = {}
        output_dict["work_flow_id"] = self.work_flow_id
        output_dict["work_serial_number"] = self.work_serial_number
        output_dict["work_name"] = self.work_name
        output_dict["add_timestamp"] = self.add_timestamp

        return output_dict

class WorkFlow(BASE):
    __tablename__ = "workflow"
    id = Column(String, nullable=False)
    user_id = Column(String, nullable=False, primary_key=True)
    name = Column(String, primary_key=True)
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
        output_dict["user_id"] = self.user_id
        output_dict["name"] = self.name
        output_dict["add_timestamp"] = self.add_timestamp

        return output_dict
