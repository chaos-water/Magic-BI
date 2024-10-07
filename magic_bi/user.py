import time
from sqlalchemy import Column, String, BigInteger
from magic_bi.db.sql_orm import BASE

class User(BASE):
    __tablename__ = "user"
    user_name: str = Column(String, primary_key=True, nullable=False)
    user_id: str = Column(String, nullable=False)
    create_timestamp: int = Column(BigInteger, nullable=False)

    def __init__(self):
        import uuid, time
        self.user_id = uuid.uuid1().hex
        self.create_timestamp = int(time.time()*1000)

    def to_json(self):
        return {"user_name": self.user_name,
                "user_id": self.user_id, "create_tiemstamp": self.create_timestamp}

