import os
import time

import uuid
from enum import Enum

from sqlalchemy import Column, String, BigInteger, Integer, TEXT

from magic_bi.db.sql_orm import BASE
from fastapi import UploadFile
from magic_bi.utils.utils import get_bytes_hash


class TrainQaFile(BASE):
    __tablename__ = "train_qa_file"
    id = Column(String, nullable=False)
    user_id = Column(String, nullable=False, primary_key=True)
    name = Column(String, primary_key=True)
    hash = Column(String, primary_key=True)
    size = Column(Integer)
    add_timestamp = Column(BigInteger, nullable=False)

    def __init__(self):
        self.id = uuid.uuid1().hex
        self.user_id = ""
        self.name = ""
        self.hash = ""
        self.size = 0
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
        output_dict["hash"] = self.hash
        output_dict["size"] = self.size
        output_dict["add_timestamp"] = self.add_timestamp

        return output_dict

    def from_upload_file(self, upload_file: UploadFile):
        self.file_bytes = upload_file.file.read()
        self.size = upload_file.size
        self.name = upload_file.filename
        self.hash = get_bytes_hash(self.file_bytes)
