import time

import uuid
from sqlalchemy import Column, String, BigInteger, Integer, TEXT, ARRAY

from magic_bi.db.sql_orm import BASE

class TrainData(BASE):
    __tablename__ = "train_data"
    id = Column(String, nullable=False)
    user_id = Column(String, nullable=False, primary_key=True)
    name = Column(String, primary_key=True)
    generate_state = Column(String)
    generate_method = Column(String)
    hash = Column(String)
    to_reach_item_cnt = Column(Integer)
    current_processed_index = Column(Integer)
    data_source_id = Column(String)
    table_list = Column(ARRAY(String))
    max_sql_len = Column(Integer)

### fewshot_relevant start
    train_qa_file_id = Column(String)
    sheet_name = Column(String)
### fewshot_relevant end

### zeroshot_relevant start
    relevant_business = Column(String)
### zeroshot_relevant end

    add_timestamp = Column(BigInteger, nullable=False)

    def __init__(self):
        self.id = uuid.uuid1().hex
        self.user_id = ""
        self.name = ""
        self.generate_state = ""
        self.hash = ""
        self.to_reach_item_cnt = 0
        self.current_processed_index = 0
        self.data_source_id = ""
        self.table_list = []
        self.max_sql_len = 0

### fewshot_relevant start
        self.train_qa_file_id = ""
        self.sheet_name = ""
### fewshot_relevant end

### zeroshot_relevant start
        self.relevant_business = ""
### zeroshot_relevant end

        self.add_timestamp = int(time.time() * 1000)
        self.file_bytes: bytes = "".encode()

    def from_dict(self, data_dict: dict):
        for key, value in data_dict.items():
            if key in self.__dict__ and value is not None:
                self.__dict__[key] = value

    def to_dict(self) -> dict:
        output_dict = {}
        output_dict["id"] = self.id
        output_dict["user_id"] = self.user_id
        output_dict["name"] = self.name
        output_dict["state"] = self.generate_state
        output_dict["hash"] = self.hash

        # output_dict["input_item_cnt"] = self.input_item_cnt
        output_dict["to_reach_item_cnt"] = self.to_reach_item_cnt
        output_dict["current_processed_index"] = self.current_processed_index


        output_dict["table_list"] = self.table_list

        output_dict["max_sql_len"] = self.max_sql_len
### fewshot_relevant start
        output_dict["train_qa_file_id"] = self.train_qa_file_id
        output_dict["sheet_name"] = self.sheet_name
### fewshot_relevant end

### zeroshot_relevant start
        output_dict["relevant_business"] = self.relevant_business
### zeroshot_relevant end
        output_dict["add_timestamp"] = self.add_timestamp

        return output_dict
