from loguru import logger
from sqlalchemy.engine.base import Engine
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import Session


TIMESCALE_BASE = declarative_base()
class TimescaleOrm():
    def __init__(self):
        self.engine: Engine = None
        self.session: Session = None

    def init(self, url: str) -> int:
        if database_exists(url) is False:
            create_database(url)

        self.engine = create_engine(url, echo=True)
        TIMESCALE_BASE.metadata.create_all(self.engine)
        self.session = Session(self.engine)

        logger.debug("TimescaleOrm init suc")
        return 0

    def exit(self):
        if self.session.is_active:
            self.session.close()

    def get_session(self) -> Session:
        if self.session.is_active is False:
            try:
                self.session.close()
                self.session = Session(self.engine)
            except Exception as e:
                logger.error("get_session failed, exception:%s" % str(e))
                return None

        return self.session

