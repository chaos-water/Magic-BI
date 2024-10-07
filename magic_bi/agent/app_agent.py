import json
from typing import List

from magic_bi.agent.memmory import Memmory
from loguru import logger

from magic_bi.agent.base_agent import BaseAgent
from magic_bi.message.message import Message
from magic_bi.utils.globals import Globals
from magic_bi.io.base_io import BaseIo
from magic_bi.agent.agent_meta import AgentMeta
from magic_bi.config.agent_config import AgentConfig
from magic_bi.app.app_api import AppApi
from typing import List, Dict
from sqlalchemy.orm.session import Session
from magic_bi.app.app import App

#
# generate_plan_prompt_template = \
# """[User Reqeust]
#     {user_question}
#
# {detail_api_description}
#
# Based on the above information, generate a plan to fulfill the user request by interacting with the system.
#
# Consider the following factors:
#     1,For the API that answers user questions, determine the required parameters. If the user does not provide them, see if they can be obtained through other APIs. If no APIs are available, ask the customer to provide the relevant information.
#     2,Try to avoid asking the customer for ID-type parameters, and instead request more easily expressible information like names.
#
# Output in the following format: [{"path": $path, "reason": "$reason"}...]. No other explanations are needed."""

evaluate_prompt_template = \
"""[History Context]
    {history_context}

{User Input}
    {user_input}

{detail_app_api_description}    

[Instructions]:
    1,

First, analyze the given conditions, then solve the problem step by step. Do not output the intermediate reasoning steps; directly output the final result.
"""

select_api_prompt_template = \
"""[User Question]
    {user_question}

{brief_api_description}

[Instructions]:
    1, Select the API that can answer the user's question;
    2, Output in the format: {"path": $path, "reason": "$reason"}. No other explanations are needed.
    
First, analyze the given conditions, then solve the problem step by step. Do not output the intermediate reasoning steps; directly output the final result."""

generate_request_prompt_template = \
"""[User Question]
    {user_question}

[App Host]
    {app_host}

[API]
    {detail_app_api_description}

[Instructions]:
    1, Fill the api.md param that can answer the user's question;
    2, Output in the following format: {"name":"$name", "path": "$path", "method": "$method", "content_type": "$content_type", "body": "$body", "reason": "$reason"}. No other explanations are needed.
    3, If the user's input question lacks necessary information, please specify what information the user needs to provide in the reason section.

First, analyze the given conditions, then solve the problem step by step. Do not output the intermediate reasoning steps; directly output the final result."""


"""
一、选择api  二、判断是否已经可以生成最终api：1、能，则推出循环；2、不能，则判断，是：a、请求其它api获取对应结果；b、让用户继续补充信息  三、生成最终api请求
"""

class AppAgent(BaseAgent):
    def __init__(self):
        self.memmory: Memmory = Memmory()
        super().__init__()

    def init(self, agent_meta: AgentMeta, agent_config: AgentConfig, globals: Globals, io: BaseIo) -> int:
        super().init(agent_meta, agent_config, globals, io)

        logger.debug("init suc")
        return 0

    def get_app_api_list_and_dict(self, app_id: str) -> (List, Dict):
        path_2_app_api_dict = {}
        try:
            with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
                app_api_list: List[AppApi] = session.query(AppApi).filter(AppApi.app_id == app_id).all()

                for app_api in app_api_list:
                    path_2_app_api_dict[app_api.path] = app_api

            logger.debug("get_app_api_list suc")
            return app_api_list, path_2_app_api_dict
        except Exception as e:
            logger.error("catch exception:%s" % str(e))
            return [], {}

    def get_brief_app_api_descriptions(self, app_api_list: List[AppApi]) -> str:
        output_api_description = ""
        index = 0
        for app_api in app_api_list:
            select_api_description_item = \
"""{api_index}:
    path: {path}
    description: {description}
    name: {name}
    \n\n""".replace("{api_index}", "[API %d]" % index).replace("{path}", app_api.path).\
            replace("{request_body}", app_api.request_body).replace("{description}", app_api.description).\
            replace("{name}", app_api.summary)

            output_api_description += select_api_description_item
            index += 1

        logger.debug("get_brief_app_api_descriptions suc")
        return output_api_description

    def get_brief_app_api_descriptions_v2(self, app_api_list: List[AppApi]) -> str:
            output_api_description = ""
            index = 0
            for app_api in app_api_list:
                request_body = json.loads(app_api.request_body)
                for content_type, value in request_body.items():
                    detail_api_description = \
                        """path: {path}
                            name: {name}
                            description: {description}
                            method: {method}
                            content_type: {content_type}
                            body: {body}\n\n""".replace("{path}", app_api.path).replace("{name}", app_api.summary) \
                            .replace("{description}", app_api.description).replace("{method}", app_api.method) \
                            .replace("{content_type}", content_type).replace("{body}", json.dumps(
                            request_body[content_type]['schema']['properties'], ensure_ascii=False))

                    output_api_description += detail_api_description
                    break

                index += 1

            logger.debug("get_brief_app_api_descriptions suc")
            return output_api_description

    def get_detail_app_api_description(self, app_api: AppApi) -> str:
        request_body = json.loads(app_api.request_body)
        for content_type, value in request_body.items():
            detail_api_description = \
"""path: {path}
    name: {name}
    description: {description}
    method: {method}
    content_type: {content_type}
    body: {body}""".replace("{path}", app_api.path).replace("{name}",app_api.summary) \
    .replace("{description}", app_api.description).replace("{method}", app_api.method)\
    .replace("{content_type}", content_type).replace("{body}", json.dumps(request_body[content_type]['schema']['properties'], ensure_ascii=False))

            logger.debug("get_detail_api_description suc")
            return detail_api_description

    def get_app(self, app_id) -> App:
        try:
            with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
                app_list: List[App] = session.query(App).filter(App.id == app_id).all()

            logger.debug("get_app suc")
            if len(app_list) > 0:
                return app_list[0]
            else:
                return None

        except Exception as e:
            logger.error("catch exception:%s" % str(e))
            return None

    def request_app(self):
        pass

    def process(self, message: Message) -> Dict:
        app: App = self.get_app(message.app_id)
        if app is None:
            logger.error("process failed")
            return

        app_api_list, path_2_app_api = self.get_app_api_list_and_dict(message.app_id)

        # detail_app_api_descriptions = self.get_brief_app_api_descriptions_v2(app_api_list)
        # generate_plan_prompt = generate_plan_prompt_template.replace("{user_question}", message.person_input).replace("{{detail_api_description}}", detail_app_api_descriptions)

        # generate_plan_prompt = generate_plan_prompt_template.replace("{user_question}",message.person_input) \
        #                                               .replace("{brief_api_description}", brief_app_api_descriptions)
        # llm_output = self.globals.general_llm_adapter.process(generate_plan_prompt)
        # generate_plan = json.loads(llm_output)
        # pass

        brief_app_api_descriptions = self.get_brief_app_api_descriptions(app_api_list)
        select_api_prompt = select_api_prompt_template.replace("{user_question}",message.person_input) \
                                                      .replace("{brief_api_description}", brief_app_api_descriptions)

        llm_output = self.globals.general_llm_adapter.process(select_api_prompt)
        selected_api = json.loads(llm_output)
        path = selected_api["path"]

        if path not in path_2_app_api:
            logger.error("could not find app_api relevant to the path:%s" % path)
            return

        app_api = path_2_app_api[path]

        detail_app_api_description = self.get_detail_app_api_description(app_api)

        generate_request_prompt = generate_request_prompt_template.replace("{user_question}", message.person_input).\
                                         replace("{app_host}", app.host).\
                                         replace("{detail_app_api_description}", detail_app_api_description)

        llm_output = self.globals.general_llm_adapter.process(generate_request_prompt)
        generate_app_api = json.loads(llm_output)

        respose = make_http_request(app.host, generate_app_api["path"], generate_app_api["method"], \
                                    generate_app_api["content_type"], generate_app_api["body"])

        logger.debug("App Agent process suc")
        return respose

def make_http_request(host, url, method, content_type, body):
    import requests
    full_url = "%s/%s" % (host.rstrip("/"), url.lstrip("/"))
    headers = {'Content-Type': content_type}

    response = requests.request(method, full_url, json=body, headers=headers)

    if response.status_code == 200:
        logger.debug("make_http_request suc, response:%s" % response.json())
        return response.json()
    else:
        logger.debug("make_http_request failed, response:%s" % response.text)
        return response.text
