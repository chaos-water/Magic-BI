from enum import Enum
import json
import time
import uuid
from typing import Dict, List
from sqlalchemy import Column, Text, String, BigInteger
# from magic_bi.db.orm import BASE
from magic_bi.db.timescale_orm import TIMESCALE_BASE


class MESSAGE_TYPE(Enum):
    AUTO = "auto"
    NO_DATA = "no_data"
    DATA = "data"


class ASSISTANT_OUTPUT_HUMAN_EVALUATION(Enum):
    GOOD = "good"
    BAD = "bad"

class Message(TIMESCALE_BASE):
    __tablename__ = "message"
    id = Column(String, primary_key=True)
    agent_id = Column(String)
    user_id = Column(String)
    person_input = Column(String)
    assistant_output = Column(Text)
    person_input_hash = Column(String)
    timestamp = Column(BigInteger)
    dataset_id = Column(String)
    file_id = Column(String)
    data_source_id = Column(String)
    app_id = Column(String)
    message_type = Column(String)
    human_evaluation = Column(String)

    def __init__(self):
        self.id: str = uuid.uuid1().hex
        self.agent_id: str = ""
        self.agent_type: str = ""
        self.person_input: str = ""
        self.assistant_output: str = ""
        self.person_input_hash: str = ""
        self.timestamp: int = int(time.time()*1000)
        self.data_source_id: str = ""
        self.dataset_id: str = ""
        self.file_id: str = ""
        self.data_id: str = ""
        self.user_id: str = ""
        self.app_id: str = ""
        self.human_evaluation: str = ""
        self.with_humman_readable_output: bool = False
        self.with_sql_cmd: bool = True
        self.with_sql_result: bool = True
        self.with_few_shot: bool = True

    def from_dict(self, input_dict: Dict):
        for key, value in input_dict.items():
            if key in self.__dict__ and value is not None:
                self.__dict__[key] = value

    def to_dict(self) -> Dict:
        return {"id": self.id, "agent_id": self.agent_id, "person_input": self.person_input}

    def is_legal(self) -> bool:
        if self.person_input == "" or (self.agent_id == "" and self.agent_type == "") or (self.dataset_id == "" and \
                                                                                    self.data_source_id == "" and \
                                                                                    self.data_id == "" and \
                                                                                    self.app_id == ""):
            return False

        return True

    def to_memory_item(self) -> Dict:
        return {"person_input": self.person_input,
                "assistant_output": self.assistant_output,
                "timestamp": self.timestamp}

    def update_hash(self):
        import hashlib
        self.person_input_hash = hashlib.sha1().update(self.person_input.encode()).hexdigest()

def copy_message(dst_message: Message, src_message: Message):
    dst_message.id = src_message.id
    dst_message.agent_id = src_message.agent_id
    dst_message.user_id = src_message.user_id
    dst_message.person_input = src_message.person_input
    dst_message.assistant_output = src_message.assistant_output
    dst_message.timestamp = src_message.timestamp
    dst_message.dataset_id = src_message.dataset_id
    dst_message.data_source_id = src_message.data_source_id