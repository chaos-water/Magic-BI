import json
from loguru import logger

from sqlalchemy.orm.session import Session
from sqlalchemy import desc

from magic_bi.utils.globals import Globals
from magic_bi.message.message import Message

SHORT_MEMORY_MAX_MESSAGE_CNT = 10
MAX_CONTEXT_SIZE = 32000

class Memmory:
    def __init__(self):
        # self.message_list: list[Message] = []
        self.agent_id: str = ""

    def init(self, globals: Globals, agent_id: str, memmory_enabled: bool) -> int:
        self.globals: Globals = globals
        self.agent_id: str = agent_id
        self.is_memmory_enabled: bool = memmory_enabled

        logger.debug("init suc")
        return 0

    # def try_truncate_memmory(self):
    #     while len(self.message_list) > SHORT_MEMORY_MAX_MESSAGE_CNT:
    #         self.message_list.pop(0)
    #
    #     logger.debug("try_truncate_memmory suc")

    def add_message(self, message: Message) -> int:
        if self.is_memmory_enabled is False:
            return 0

        with self.globals.timescale_orm.get_session() as session:
            tmp_message: Message = Message()
            tmp_message.agent_id = message.agent_id
            from magic_bi.message.message import copy_message
            copy_message(tmp_message, message)

            session.add(tmp_message)
            session.commit()

        logger.debug("add_message suc")
        return 0

    def try_get_exact_message(self, input_message: Message) -> Message:
        with self.globals.timescale_orm.get_session() as session:
            message_list: list[Message] = session.query(Message).filter(Message.data_source_id == input_message.data_source_id).\
                filter(Message.dataset_id == input_message.dataset_id).filter(Message.person_input_hash == input_message.person_input_hash).\
                limit(1).all()
            if len(message_list) > 0:
                logger.debug("try_get_exact_memmory suc, get exact memmory getted")
                return message_list[0]

        logger.debug("try_get_exact_memmory failed, no exact memmory getted")
        return None

    def get_memory_str(self, current_prompt_size: int=4096) -> str:
        memory_str = ""
        with Session(self.globals.sql_orm.engine) as session:
            message_list: list[Message] = session.query(Message).filter(Message.agent_id == self.agent_id).order_by(desc(Message.timestamp)).limit(1).all()
            for message in message_list:
                memory_item = json.dumps(message.to_memory_item(), ensure_ascii=False)
                if len(memory_str) + len(memory_item) + current_prompt_size > self.context_size:
                    break
                memory_str += memory_item + "\n"

        logger.debug("get_memory_str suc, memory context_size:%d" % len(memory_str))
        return memory_str
