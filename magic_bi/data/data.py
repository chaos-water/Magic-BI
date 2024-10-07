import os
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
    IMAGE = "image"
    VIDEO = "video"

def get_supported_doc_types() -> list[str]:
    supported_doc_types = ["docx", "pdf", "txt"]
    return supported_doc_types

def get_supported_image_types() -> list[str]:
    supported_doc_types = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.tiff']
    return supported_doc_types

def get_supported_video_types() -> list[str]:
    supported_doc_types = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.mpeg', '.mpg', '.m4v', '.3gp', '.ts']
    return supported_doc_types

class Data(BASE):
    __tablename__ = "data"
    id = Column(String, nullable=False)
    dataset_id = Column(String, nullable=False, primary_key=True)
    user_id = Column(String, nullable=False, primary_key=True)
    name = Column(String, primary_key=True)
    hash = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    size = Column(Integer)
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

    def from_upload_file(self, upload_file: UploadFile):
        self.file_bytes = upload_file.file.read()
        self.type = DATA_TYPE.DOC.value
        self.size = upload_file.size
        self.name = upload_file.filename
        self.hash = get_bytes_hash(self.file_bytes)


    def get_content(self):
        pass

