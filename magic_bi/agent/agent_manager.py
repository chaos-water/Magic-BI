from loguru import logger
from typing import List
from sqlalchemy.orm import Session
# from magic_bi.agent.role_play.role_play_agent import RolePlayAgent, AgentMeta
from magic_bi.agent.base_agent import AgentMeta
from magic_bi.utils.globals import Globals
from magic_bi.io.base_io import BaseIo
# from magic_bi.agent.agent_factory import get_agent
from magic_bi.agent.agent_type import AGENT_TYPE
from magic_bi.config.global_config import GlobalConfig
from magic_bi.agent.base_agent import BaseAgent
# from magic_bi.agent_manager.gui_agent_manager import GuiAgentManager

class AgentManager():

    def __init__(self, global_config: GlobalConfig, globals: Globals):
        self.global_config = global_config
        self.globals: Globals = globals
        # self.gui_agent_manager = GuiAgentManager()

    # def create_v2(self, agent_meta: AgentMeta) -> AgentMeta:
    #     try:
    #         with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
    #             session.add(agent_meta)
    #             session.commit()
    #     except Exception as e:
    #         logger.exception(e)
    #         return None
    #
    #     logger.debug("create_v2 suc, agent_meta:%s" % agent_meta.__dict__)
    #     return agent_meta

    def get(self, user_id: str) -> List[AgentMeta]:
        with Session(self.globals.sql_orm.engine) as session:
            agent_meta_list: List[AgentMeta] = session.query(AgentMeta).filter(AgentMeta.user_id == user_id).all()

        logger.debug("list suc, agent_meta cnt:%d" % len(agent_meta_list))
        return agent_meta_list

    # def delete_v2(self, agent_meta: AgentMeta) -> int:
    #     with Session(self.globals.sql_orm.engine) as session:
    #         session.query(AgentMeta).filter(AgentMeta.id == agent_meta.id).delete()
    #         session.commit()
    #
    #     logger.debug("delete_by_id suc, id:%s" % id)
    #     return 0


    # def create_batch(self, config_path: str, io: BaseIo, timestamp_callback: Callable) -> Dict[str, RolePlayAgent]:
    #     agent_dicts: [str, RolePlayAgent] = {}
    #     yaml_content = get_yaml_content(config_path)
    #     for _, agent_meta_dict in yaml_content.items():
    #         agent = self.create(agent_meta_dict, io, timestamp_callback)
    #         agent_dicts[agent.meta.name] = agent
    #
    #     logger.debug("create_batch suc, agents cnt:%d" % len(agent_dicts))
    #     return agent_dicts

    # def add(self, agent_meta: AgentMeta, yaml_content: Dict[str, Any], io: BaseIo, timestamp_callback: Callable) -> int:
    def add(self, agent_meta: AgentMeta) -> int:
        # agent_meta: AgentMeta = AgentMeta()
        # for key, value in yaml_content.items():
        #     if key == "memories" or value is None:
        #         continue
        #
        #     agent_meta.__dict__[key] = value

        # agent: RolePlayAgent = RolePlayAgent(agent_meta=agent_meta, globals=self.globals,
        #                                                 io=io, timestamp_callback=timestamp_callback)
        # if "memories" in yaml_content:
        #     agent.memory_operator.from_list(yaml_content["memories"])

        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            session.add(agent_meta)
            session.commit()

        logger.debug("create suc, agent_meta id:%s" % agent_meta.id)
        return agent_meta


    def delete(self, agent_name: str):
        with Session(self.globals.sql_orm.engine) as session:
            session.query(AgentMeta).filter(AgentMeta.name == agent_name).delete()
            session.commit()

        logger.debug("delete suc, agent_name:%s" % agent_name)

    def get_by_id(self, id: str, io: BaseIo) -> BaseAgent:
        with Session(self.globals.sql_orm.engine) as session:
            agent_meta_list: List[AgentMeta] = session.query(AgentMeta).filter(AgentMeta.id==id).all()
            if len(agent_meta_list) == 0:
                logger.error("get_by_id failed")
                return None

            agent_meta: AgentMeta = agent_meta_list[0]
            agent: BaseAgent = self.get_agent(agent_meta=agent_meta, agent_config=self.global_config.agent_config, globals=self.globals, io=io)

            logger.debug("get_by_id suc")
            return agent


    def get_agent(self, id: str, io: BaseIo) -> BaseAgent:
        with Session(self.globals.sql_orm.engine) as session:
            agent_meta_list: List[AgentMeta] = session.query(AgentMeta).filter(AgentMeta.id == id).all()
            if len(agent_meta_list) == 0:
                logger.error("get_agent failed, no qualified agent")
                return None

            agent_meta: AgentMeta = agent_meta_list[0]
            if agent_meta.type == AGENT_TYPE.PANDAS.value:
                from magic_bi.agent.pandas_agent import PandasAgent
                from magic_bi.utils.globals import GLOBALS
                pandas_agent: PandasAgent = PandasAgent()
                pandas_agent.init(agent_meta, GLOBALS, io)

                logger.debug("get_agent suc")
                return pandas_agent
            else:
                logger.error("get_agent failed")
                return None

    def get_agent_by_type(self, agent_type: str, io: BaseIo) -> BaseAgent:
        agent_meta: AgentMeta = AgentMeta()
        agent_meta.type = agent_type

        if agent_meta.type == AGENT_TYPE.PANDAS.value:
            from magic_bi.agent.pandas_agent import PandasAgent
            from magic_bi.utils.globals import GLOBALS
            pandas_agent: PandasAgent = PandasAgent()
            pandas_agent.init(agent_meta, GLOBALS, io)

            logger.debug("get_agent suc")
            return pandas_agent

        elif agent_meta.type == AGENT_TYPE.SQL_BY_PUBLIC_LLM.value:
            from magic_bi.agent.general_llm_sql_agent import GeneralLlmSqlAgent
            from magic_bi.utils.globals import GLOBALS
            sql_agent: GeneralLlmSqlAgent = GeneralLlmSqlAgent()
            sql_agent.init(agent_meta, GLOBALS, io)

            logger.debug("get_agent suc")
            return sql_agent

        elif agent_meta.type == AGENT_TYPE.SQL_BY_FINETUNE_LLM.value:
            from magic_bi.agent.finetuned_llm_sql_agent import FinetunedLlmSqlAgent
            from magic_bi.utils.globals import GLOBALS
            sql_agent: FinetunedLlmSqlAgent = FinetunedLlmSqlAgent()
            sql_agent.init(agent_meta, self.global_config.agent_config, self.globals, io, self.global_config.misc_config.get_language_name())

            logger.debug("get_agent suc")
            return sql_agent

        elif agent_meta.type == AGENT_TYPE.SQL_BY_FINETUNE_LLM.value:
            from magic_bi.agent.finetuned_llm_sql_agent import FinetunedLlmSqlAgent
            from magic_bi.utils.globals import GLOBALS
            sql_agent: FinetunedLlmSqlAgent = FinetunedLlmSqlAgent()
            sql_agent.init(agent_meta, GLOBALS, io)

            logger.debug("get_agent suc")
            return sql_agent
        elif agent_meta.type in (AGENT_TYPE.SQL_BY_FINETUNE_LLM.value, AGENT_TYPE.SQL.value):
            from magic_bi.agent.finetuned_llm_sql_agent import FinetunedLlmSqlAgent
            from magic_bi.utils.globals import GLOBALS
            sql_agent: FinetunedLlmSqlAgent = FinetunedLlmSqlAgent()
            sql_agent.init(agent_meta, self.global_config.agent_config, GLOBALS, io, self.global_config.misc_config.get_language_name())

            logger.debug("get_agent suc")
            return sql_agent

        elif agent_meta.type == AGENT_TYPE.RAG.value:
            from magic_bi.agent.rag_agent import RagAgent
            from magic_bi.utils.globals import GLOBALS
            rag_agent: RagAgent = RagAgent()
            rag_agent.init(agent_meta, self.global_config.agent_config, GLOBALS, io, self.global_config.misc_config.get_language_name())

            logger.debug("get_agent suc")
            return rag_agent

        elif agent_meta.type == AGENT_TYPE.APP.value:
            from magic_bi.agent.app_agent import AppAgent
            from magic_bi.utils.globals import GLOBALS
            app_agent: AppAgent = AppAgent()
            app_agent.init(agent_meta, self.global_config.agent_config, GLOBALS, io)

            logger.debug("get_agent suc")
            return app_agent

        else:
            logger.error("get_agent failed")
            return None

    def get_agent_meta(self, user_id: str) -> List[AgentMeta]:
        agent_meta_list = []
        with Session(self.globals.sql_orm.engine) as session:
            # results: List[AgentMeta] = session.query(AgentMeta).filter(AgentMeta.name == agent_name).\
            #     filter(AgentMeta.sandbox_id == sandbox_id).all()
            agent_meta_list: List[AgentMeta] = session.query(AgentMeta).filter(AgentMeta.user_id == user_id).all()
            # if len(agent_meta_list) == 0:
            #     return None

            # agent_meta: AgentMeta = results[0]
            # agent: RolePlayAgent = RolePlayAgent(agent_meta=agent_meta, globals=self.globals,
            #                                                 io=io, timestamp_callback=timestamp_callback)

            logger.debug("get_agent_meta suc, agent_meta cnt:%d" % len(agent_meta_list))
            # return agent_meta
            return agent_meta_list

    # def get_or_create(self, yaml_content: Dict[str, Any], io: BaseIo, timestamp_callback: Callable, sandbox_id: str) -> RolePlayAgent:
    #     agent_name = yaml_content.get("name", "")
    #     agent: RolePlayAgent = self.get(agent_name, sandbox_id, io, timestamp_callback)
    #     if agent is None:
    #         agent: RolePlayAgent = self.create(yaml_content, io, timestamp_callback)
    #
    #     logger.debug("get_or_create suc, agent_name: %s" % agent_name)
    #     return agent
    #
    # def get_or_create_batch(self, config_path: str, io: BaseIo, timestamp_callback: Callable, sandbox_id: str) -> Dict[str, RolePlayAgent]:
    #     agent_dicts: [str, RolePlayAgent] = {}
    #     yaml_content = get_yaml_content(config_path)
    #     for _, agent_meta_dict in yaml_content.items():
    #         agent_meta_dict["sandbox_id"] = sandbox_id
    #         agent: RolePlayAgent = self.get_or_create(agent_meta_dict, io, timestamp_callback, sandbox_id)
    #         agent_dicts[agent.meta.name] = agent
    #
    #     logger.debug("get_or_create_batch suc, agent cnt:%d" % len(agent_dicts))
    #     return agent_dicts

    # def start(self, agent_meta: AgentMeta) -> int:
    #     if agent_meta.type == AGENT_TYPE.GUI.value:
    #         self.gui_agent_manager.start(agent_meta)
    #     # with Session(self.globals.sql_orm.engine) as session:
    #     #     session.query(AgentMeta).filter(AgentMeta.id == agent_meta.id).delete()
    #     #     session.commit()
    #
    #     logger.debug("delete_by_id suc, id:%s" % id)
    #     return 0
    #
    # def stop(self, agent_meta: AgentMeta) -> int:
    #     if agent_meta.type == AGENT_TYPE.GUI.value:
    #         self.gui_agent_manager.stop(agent_meta)
    #
    #     # with Session(self.globals.sql_orm.engine) as session:
    #     #     session.query(AgentMeta).filter(AgentMeta.id == agent_meta.id).delete()
    #     #     session.commit()
    #
    #     logger.debug("delete_by_id suc, id:%s" % id)
    #     return 0

    def get_status(self, agent_meta: AgentMeta) -> int:
        # if agent_meta.type == AGENT_TYPE.GUI.value:
        #     self.gui_agent_manager.start(agent_meta)

        # with Session(self.globals.sql_orm.engine) as session:
        #     session.query(AgentMeta).filter(AgentMeta.id == agent_meta.id).delete()
        #     session.commit()

        logger.debug("get_status suc, id:%s" % id)
        return 0
