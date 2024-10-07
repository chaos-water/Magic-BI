import json
import uuid
from sqlalchemy import Column, String, BigInteger, Integer, ForeignKey, Text
from loguru import logger
import time

from typing import Dict, Any
from magic_bi.db.sql_orm import BASE
from magic_bi.agent.agent_type import AGENT_TYPE

from enum import Enum

class LLM_TRANSACTION_TYPE(Enum):
    GENERATE_SQL = "generate_sql"
    SELECT_TABLE_FROM_REFENCED_TABLE = "select_table_from_referenced_table"
    SELECT_TABLE_BY_LLM_GUESS = "select_table_by_llm_guess"

class HUMMAN_EVALUATION(Enum):
    GOOD = "good"
    BAD = "bad"


class LlmTransaction(BASE):
    __tablename__ = "llm_transaction"
    id = Column(String, nullable=False, primary_key=True)
    type = Column(String, nullable=False)
    llm_input = Column(Text, nullable=False)
    llm_output = Column(Text, nullable=False)
    human_evaluation = Column(String)
    add_timestamp = Column(BigInteger)

    def __init__(self):
        self.id = uuid.uuid1().hex
        self.type = ""
        self.llm_input = ""
        self.llm_input = ""
        self.human_evaluation = ""
        self.message_id = ""
        self.add_timestamp = int(time.time() * 1000)


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
