import time
import uuid
from typing import Dict
from sqlalchemy import Column, String, BigInteger

from magic_bi.db.sql_orm import BASE


class DomainKnowledge(BASE):
    __tablename__ = "domain_knowledge"
    id = Column(String, nullable=False)
    data_connector_id = Column(String, nullable=False, primary_key=True)
    content = Column(String, nullable=False, primary_key=True)
    add_timestamp = Column(BigInteger, nullable=False)

    def __init__(self):
        self.id = uuid.uuid1().hex
        self.data_connector_id = ""
        self.content = ""
        self.add_timestamp = int(time.time() * 1000)

    def from_dict(self, body: Dict):
        self.id = body.get("id", "")
        if self.id == "":
            self.id = uuid.uuid1().hex

        self.data_connector_id = body.get("data_connector_id", "")
        self.content = body.get("content", "")
        self.add_timestamp = int(time.time() * 1000)

    def to_dict(self):
        output = {"id": self.id, "data_connector_id": self.data_connector_id, "content": self.content, "add_timestamp": self.add_timestamp}
        return output