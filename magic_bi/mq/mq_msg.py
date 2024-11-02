import json
from enum import Enum

class MQ_MSG_TYPE(Enum):
    START_GENERATE_TRAIN_DATA = "start_generate_train_data"
    RESUME_GENERATE_TRAIN_DATA = "resume_generate_train_data"
    TRAIN_MODEL = "train_model"
    DEPLOY_MODEL = "deploy_model"

class MqMsg():
    def __init__(self):
        self.msg_type: str = ""
        self.msg_json: dict = {}

    def to_json_str(self) -> str:
        return json.dumps({"msg_type": self.msg_type, "msg": self.msg_json})

    def from_json_str(self, json_str: str):
        input_json = json.loads(json_str)
        self.msg_type = input_json["msg_type"]
        self.msg_json = input_json["msg"]
