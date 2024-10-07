import json
import uuid
from sqlalchemy import Column, String, BigInteger, Integer
from loguru import logger
import time

from typing import Dict, Any
from magic_bi.db.sql_orm import BASE
from magic_bi.agent.agent_type import AGENT_TYPE


class AgentMeta(BASE):
    __tablename__ = "agent_meta"
    user_id = Column(String, primary_key=True, nullable=False)
    name = Column(String, primary_key=True, nullable=False)
    id = Column(String, nullable=False)
    intro = Column(String)
    type = Column(String, nullable=False)
    add_timestamp = Column(BigInteger, nullable=False)
    status = Column(String, nullable=False)

    def __init__(self):
        self.id = uuid.uuid1().hex
        self.name = ""
        self.user_id = ""
        self.intro = ""
        self.type = ""
        self.add_timestamp = int(time.time() * 1000)
        self.status = ""
        self.max_retry_cnt: int = 5

    def from_str(self, input_str: str) -> int:
        if input_str is None:
            return -1

        input_dict = json.loads(input_str)
        self.from_dict(input_dict)
        return 0

    def from_dict(self, input_dict: Dict) -> int:
        for key, value in input_dict.items():
            if key in self.__dict__ and value is not None:
                self.__dict__[key] =  value

        if self.type not in [item.value for item in AGENT_TYPE]:
            logger.error("unsupported agent_type:%s" % self.type)
            return -1

        logger.debug("from_dict suc")
        return 0

    def to_dict(self) -> Dict:
        output_dict = {}
        for key, value in self.__dict__.items():
            if key.startswith("_"):
                continue
            output_dict[key] = value

        return output_dict
