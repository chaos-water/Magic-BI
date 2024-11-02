import time
import uuid

from sqlalchemy import Column, String, BigInteger

from magic_bi.db.sql_orm import BASE


class TableDescription(BASE):
    __tablename__ = "table_description"
    id = Column(String, nullable=False)
    data_source_id = Column(String, nullable=False, primary_key=True)
    table_name = Column(String, nullable=False, primary_key=True)
    table_description = Column(String, nullable=False)
    add_timestamp = Column(BigInteger, nullable=False)

    def __init__(self):
        self.id = uuid.uuid1().hex
        self.data_source_id = ""
        self.table_name = ""
        self.table_description = ""
        self.add_timestamp = int(time.time() * 1000)

    def from_dict(self, body: dict):
        self.id = body.get("id", "")
        if self.id == "":
            self.id = uuid.uuid1().hex

        self.data_source_id = body.get("data_source_id", "")
        self.table_name = body.get("table_name", "")
        self.table_description = body.get("table_description", "")
        self.add_timestamp = int(time.time() * 1000)