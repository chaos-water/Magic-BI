import json

from loguru import logger
from fastapi import APIRouter, Request, WebSocket
from fastapi.responses import JSONResponse

from typing import Dict, List
from magic_bi.utils.globals import GLOBALS, GLOBAL_CONFIG
from magic_bi.utils.utils import get_http_rsp
from magic_bi.agent.agent_manager import AgentManager
from magic_bi.io.websocket_io import WebsocketIo
from magic_bi.agent.base_agent import BaseAgent
from magic_bi.agent.base_agent import AgentMeta
from magic_bi.message.message import Message
from magic_bi.agent.utils import try_divide_user_question, merge_sub_question_answer

AGENT_MANAGER = AgentManager(global_config=GLOBAL_CONFIG, globals=GLOBALS)

# url_prefix = "magic_bi"
url_prefix = GLOBAL_CONFIG.web_config.url_prefix

def create_agent_router(prefix: str):
    agent_router = APIRouter(prefix=prefix)

    @agent_router.options("/{path:path}")
    async def preflight_handler(request: Request):
        response = JSONResponse(content="")
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    @agent_router.post("/agent/add")
    def add_agent(body: Dict):
        agent_meta = AgentMeta()
        agent_meta.from_dict(body)
        agent_meta = AGENT_MANAGER.add(agent_meta=agent_meta)
        if agent_meta == 0:
            logger.debug("add_agent suc, agent_id:%s" % agent_meta.id)
            return get_http_rsp(data={"id": agent_meta.id})
        else:
            logger.error("add_agent failed, input_body:%s" % body)
            return get_http_rsp(code=-1, msg="failed")

    @agent_router.post("/agent/delete")
    def delete_agent(body: Dict):
        agent_meta = AgentMeta()
        agent_meta.from_dict(body)
        ret = AGENT_MANAGER.delete_v2(agent_meta=agent_meta)
        if ret == 0:
            logger.debug("delete_agent suc, agent_id:%s" % id)
            return get_http_rsp()
        else:
            logger.error("delete_agent failed, agent_id:%s" % id)
            return get_http_rsp(code=ret, msg="failed")

    @agent_router.post("/agent/get_status")
    def get_agent_status(body: Dict):
        agent_meta_list: List[AgentMeta] = AGENT_MANAGER.list()
        logger.debug("list suc, agent_meta cnt:%s" % len(agent_meta_list))
        return get_http_rsp(data=agent_meta_list)

    @agent_router.post("/agent/get")
    def get_agent(request: Request, body: Dict):
        user_id = request.headers.get("user_id")
        # user_id = body.get("user_id")

        agent_meta_list: List[AgentMeta] = AGENT_MANAGER.get(user_id)
        logger.debug("get suc, agent_meta cnt:%d" % len(agent_meta_list))
        return get_http_rsp(data=agent_meta_list)

    @agent_router.post("/agent/process")
    def agent_process(body: Dict):
        message = Message()
        message.from_dict(body)
        if message.is_legal() is False:
            logger.error("message is illegal:%s" % message.to_dict())
            return get_http_rsp(code=-1, msg="message is illegal")

        if len(message.agent_id) > 0:
            agent: BaseAgent = AGENT_MANAGER.get_agent(message.agent_id, None)
        elif len(message.agent_type) > 0:
            agent: BaseAgent = AGENT_MANAGER.get_agent_by_type(message.agent_type, None)
        else:
            logger.error("agent_process failed")
            return get_http_rsp(code=-1, msg="unknown agent_type")

        from magic_bi.agent.agent_type import AGENT_TYPE
        if message.agent_type == AGENT_TYPE.SQL_BY_PUBLIC_LLM.value:
            sql_output, human_readable_output, sql_cmd, relevant_table_list, relevant_table_descriptions, \
                relevant_qa_template, relevant_domain_knowledge = agent.process(message)

            logger.debug("agent_process suc")
            ret_data = {"sql_output": sql_output, "human_readable_output": human_readable_output, "sql_cmd": sql_cmd, \
                        "relevant_table_descriptions": relevant_table_descriptions, "relevant_qa_template":relevant_qa_template,
                        "relevant_domain_knowledge": relevant_domain_knowledge}
            return get_http_rsp(data=ret_data)

        elif message.agent_type == AGENT_TYPE.SQL_BY_FINETUNE_LLM.value:
            if GLOBAL_CONFIG.agent_config.try_decompose_user_question:
                sub_questions, merge_strategy = try_divide_user_question(message.person_input, GLOBALS.general_llm_adapter)
            else:
                sub_questions = []
                merge_strategy = ""

            if len(sub_questions) == 0 or len(merge_strategy) == 0:
                sql_output, human_readable_output, sql_cmd = agent.process(message)
            else:
                original_user_question = message.person_input
                sub_question_2_sql_output_dict = {}
                for sub_question in sub_questions:
                    message.person_input = sub_question
                    sql_output, human_readable_output, sql_cmd = agent.process(message)
                    sub_question_2_sql_output_dict[sub_question] = sql_output

                merge_sub_question_answer(original_user_question, sub_question_2_sql_output_dict, GLOBALS.general_llm_adapter)

            logger.debug("agent_process suc")
            ret_data = {"sql_output": sql_output, "human_readable_output": human_readable_output, "sql_cmd": sql_cmd}
            return get_http_rsp(data=ret_data)

        elif message.agent_type == AGENT_TYPE.RAG.value:
            answer, relevant_content_chunks = agent.process(message)

            logger.debug("agent_process suc")
            ret_data = {"answer": answer, "relevant_content_chunks": relevant_content_chunks}
            return get_http_rsp(data=ret_data)

        elif message.agent_type == AGENT_TYPE.APP.value:
            answer = agent.process(message)

            logger.debug("agent_process suc")
            ret_data = {"answer": answer}
            return get_http_rsp(data=ret_data)

    @agent_router.websocket("/agent/process")
    async def agent_process(websocket: WebSocket):
        await websocket.accept()
        data_str: str = await websocket.receive_text()
        data: Dict = json.loads(data_str)
        agent_id = data.get("id", "")
        if agent_id == "":
            logger.error("agent_id is blank")
            return

        websocket_io: WebsocketIo = WebsocketIo(websocket=websocket)
        agent: BaseAgent = AGENT_MANAGER.get_by_id(id=agent_id, io=websocket_io)
        agent.init()
        agent.run()

    return agent_router
