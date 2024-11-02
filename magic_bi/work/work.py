import uuid

import time

from sqlalchemy import Column, String, BigInteger, Integer, TEXT

from magic_bi.db.sql_orm import BASE

class WorkOutput():
    def __init__(self):
        self.code: int = 0
        self.data: any = ''
        self.msg: str = ''

class WorkInput():
    def __init__(self):
### text input
        self.user_input: str = ""
        self.previous_work_output: str = ""

        self.text_content: str = ""
        self.file_base64_list: list[str] = ""
        self.file_id: str = ""
        self.dataset_id: str = ""
        self.data_source_id: str = ""


class Work(BASE):
    __tablename__ = "work"
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

    # def from_upload_file(self, upload_file: UploadFile):
    #     self.file_bytes = upload_file.file.read()
    #     self.type = DATA_TYPE.DOC.value
    #     self.size = upload_file.size
    #     self.name = upload_file.filename
    #     self.hash = get_bytes_hash(self.file_bytes)
    #
    #
    # def get_content(self):
    #     pass


# class Work(ABC):
#     def __init__(self):
#         pass
#
#     def execute(self):
#         pass
