from loguru import logger
from sqlalchemy.orm import Session
from magic_bi.agent.base_agent import AgentMeta
from magic_bi.utils.globals import Globals
from magic_bi.io.base_io import BaseIo
from magic_bi.agent.agent_type import AGENT_TYPE
from magic_bi.config.global_config import GlobalConfig
from magic_bi.agent.base_agent import BaseAgent

class AgentManager():

    def __init__(self, global_config: GlobalConfig, globals: Globals):
        self.global_config = global_config
        self.globals: Globals = globals

    def get(self, user_id: str) -> list[AgentMeta]:
        with Session(self.globals.sql_orm.engine) as session:
            agent_meta_list: list[AgentMeta] = session.query(AgentMeta).filter(AgentMeta.user_id == user_id).all()

        logger.debug("list suc, agent_meta cnt:%d" % len(agent_meta_list))
        return agent_meta_list

    def add(self, agent_meta: AgentMeta) -> int:
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
            agent_meta_list: list[AgentMeta] = session.query(AgentMeta).filter(AgentMeta.id==id).all()
            if len(agent_meta_list) == 0:
                logger.error("get_by_id failed")
                return None

            agent_meta: AgentMeta = agent_meta_list[0]
            agent: BaseAgent = self.get_agent(agent_meta=agent_meta, agent_config=self.global_config.agent_config, globals=self.globals, io=io)

            logger.debug("get_by_id suc")
            return agent

    def get_agent_by_type(self, agent_type: str, io: BaseIo) -> BaseAgent:
        agent_meta: AgentMeta = AgentMeta()
        agent_meta.type = agent_type

        if agent_meta.type == AGENT_TYPE.SQL_BY_GENERAL_LLM.value:
            from magic_bi.agent.sql.general_llm_sql_agent import GeneralLlmSqlAgent
            from magic_bi.utils.globals import GLOBALS
            sql_agent: GeneralLlmSqlAgent = GeneralLlmSqlAgent()
            sql_agent.init(agent_meta, GLOBALS, io)

            logger.debug("get_agent suc")
            return sql_agent

        elif agent_meta.type == AGENT_TYPE.SQL_BY_FINETUNE_LLM.value:
            from magic_bi.agent.sql.finetuned_llm_sql_agent import FinetunedLlmSqlAgent
            from magic_bi.utils.globals import GLOBALS
            sql_agent: FinetunedLlmSqlAgent = FinetunedLlmSqlAgent()
            sql_agent.init(agent_meta, self.global_config.agent_config, self.globals, io, self.global_config.system_config.get_language_name())

            logger.debug("get_agent suc")
            return sql_agent

        elif agent_meta.type == AGENT_TYPE.SQL_BY_FINETUNE_LLM.value:
            from magic_bi.agent.sql.finetuned_llm_sql_agent import FinetunedLlmSqlAgent
            from magic_bi.utils.globals import GLOBALS
            sql_agent: FinetunedLlmSqlAgent = FinetunedLlmSqlAgent()
            sql_agent.init(agent_meta, GLOBALS, io)

            logger.debug("get_agent suc")
            return sql_agent
        elif agent_meta.type in (AGENT_TYPE.SQL_BY_FINETUNE_LLM.value, AGENT_TYPE.SQL.value):
            from magic_bi.agent.sql.finetuned_llm_sql_agent import FinetunedLlmSqlAgent
            from magic_bi.utils.globals import GLOBALS
            sql_agent: FinetunedLlmSqlAgent = FinetunedLlmSqlAgent()
            sql_agent.init(agent_meta, self.global_config.agent_config, GLOBALS, io, self.global_config.system_config.get_language_name())

            logger.debug("get_agent suc")
            return sql_agent

        elif agent_meta.type == AGENT_TYPE.RAG.value:
            from magic_bi.agent.rag.rag_agent import RagAgent
            from magic_bi.utils.globals import GLOBALS
            rag_agent: RagAgent = RagAgent()
            rag_agent.init(agent_meta, self.global_config.agent_config, GLOBALS, io, self.global_config.system_config.get_language_name())

            logger.debug("get_agent suc")
            return rag_agent

        elif agent_meta.type == AGENT_TYPE.APP_BY_GENERAL_LLM.value:
            from magic_bi.agent.app.general_llm_app_agent_plan import GeneralLlmAppAgent
            from magic_bi.utils.globals import GLOBALS
            app_agent: GeneralLlmAppAgent = GeneralLlmAppAgent()
            app_agent.init(agent_meta, self.global_config.agent_config, GLOBALS, io, self.global_config.system_config.get_language_name())

            logger.debug("get_agent suc")
            return app_agent

        elif agent_meta.type == AGENT_TYPE.WORK_FLOW.value:
            from magic_bi.agent.work_flow_agent import WorkFlowAgent
            from magic_bi.utils.globals import GLOBALS
            work_flow_agent: WorkFlowAgent = WorkFlowAgent()

            logger.debug("get_agent suc")
            return work_flow_agent

        else:
            logger.error("get_agent failed")
            return None

    def get_agent_meta(self, user_id: str) -> list[AgentMeta]:
        agent_meta_list = []
        with Session(self.globals.sql_orm.engine) as session:
            # results: list[AgentMeta] = session.query(AgentMeta).filter(AgentMeta.name == agent_name).\
            #     filter(AgentMeta.sandbox_id == sandbox_id).all()
            agent_meta_list: list[AgentMeta] = session.query(AgentMeta).filter(AgentMeta.user_id == user_id).all()
            # if len(agent_meta_list) == 0:
            #     return None

            # agent_meta: AgentMeta = results[0]
            # agent: RolePlayAgent = RolePlayAgent(agent_meta=agent_meta, globals=self.globals,
            #                                                 io=io, timestamp_callback=timestamp_callback)

            logger.debug("get_agent_meta suc, agent_meta cnt:%d" % len(agent_meta_list))
            # return agent_meta
            return agent_meta_list



    def get_status(self, agent_meta: AgentMeta) -> int:
        # if agent_meta.type == AGENT_TYPE.GUI.value:
        #     self.gui_agent_manager.start(agent_meta)

        # with Session(self.globals.sql_orm.engine) as session:
        #     session.query(AgentMeta).filter(AgentMeta.id == agent_meta.id).delete()
        #     session.commit()

        logger.debug("get_status suc, id:%s" % id)
        return 0
