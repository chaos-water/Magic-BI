import time
import uuid
from typing import Dict
from sqlalchemy import Column, String, BigInteger

from magic_bi.db.sql_orm import BASE


class QaTemplate(BASE):
    __tablename__ = "qa_template"
    id = Column(String, nullable=False)
    data_source_id = Column(String, nullable=False, primary_key=True)
    question = Column(String, nullable=False, primary_key=True)
    answer = Column(String, nullable=False)
    add_timestamp = Column(BigInteger, nullable=False)

    def __init__(self):
        self.id = uuid.uuid1().hex
        self.data_source_id = ""
        self.question = ""
        self.answer = ""
        self.add_timestamp = int(time.time() * 1000)

    def from_dict(self, body: Dict):
        self.id = body.get("id", "")
        if self.id == "":
            self.id = uuid.uuid1().hex

        self.data_source_id = body.get("data_source_id", "")
        self.question = body.get("question", "")
        self.answer = body.get("answer", "")
        self.add_timestamp = int(time.time() * 1000)