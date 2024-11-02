import json

from loguru import logger
from sqlalchemy.orm.session import Session
from sqlalchemy import desc

from magic_bi.utils.globals import Globals

user_portrait_by_message_prompt_template = '''
[USER HISTORY MESSAGES]
{user_history_messages}

[OUTPUT TEMPLATE]
["tag1", "tag2", "tag3"...]

Based on the above, generate 10 tags as the portrait of the user which is used to recommend info to the user.
'''

class UserPortrait:
    def __init__(self):
        self.globals: Globals = None

    def init(self, globals: Globals) -> int:
        self.globals: Globals = globals

        logger.debug("init suc")
        return 0

    def get_user_portrait(self, user_id: str) -> list:
        user_portrait: list = []
        user_input_list_str: str = ""

        from magic_bi.message.message import Message
        import datetime

        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            message_list: list[Message] = session.query(Message).filter(Message.user_id == user_id).order_by(desc(Message.timestamp)).limit(10).all()
            for message in message_list:
                user_input = "%s %s\n" % (datetime.datetime.fromtimestamp(message.timestamp).strftime("%Y-%m-%d %H:%M:%S"), message.person_input)
                user_input_list_str += user_input

        prompt = user_portrait_by_message_prompt_template.format("user_history_messages", user_input_list_str)
        llm_output = self.globals.general_llm_adapter.process(prompt)

        try:
            user_portrait = json.loads(llm_output)
        except Exception as e:
            logger.error("catch exception:%s" % str(e))
            logger.error("llm_output:%s" % llm_output)

        logger.debug("get_user_portrait suc")
        return user_portrait
