import json


from magic_bi.agent.memmory import Memmory
from loguru import logger

from magic_bi.agent.base_agent import BaseAgent
from magic_bi.message.message import Message
from magic_bi.utils.globals import Globals
from magic_bi.io.base_io import BaseIo
from magic_bi.agent.agent_meta import AgentMeta
from magic_bi.app.app_api import AppApi
from sqlalchemy.orm.session import Session
from magic_bi.app.app import App
from magic_bi.config.system_config import SystemConfig


select_api_prompt_template = \
    """[User Question]
        {user_question}
    
    {brief_api_description}
    
    [Instructions]:
        1, Select the API that can answer the user's question;
        2, Output in the format: {"path": $path, "reason": "$reason"}. No other explanations are needed.
    
    First, analyze the given conditions, then solve the problem step by step. Do not output the intermediate reasoning steps; directly output the final result."""

generate_request_prompt_template = \
"""[Historical Context]:
    {historical_context}

[Task]:
    {task}

[API]
    {detail_app_api_description}

[Instructions]:
    1, Fill the api param that can answer the user's question;
    2, Output in the following format: {"name":"$name", "path": "$path", "method": "$method", "content_type": "$content_type", "body": "$body", "reason": "$reason"}. No other explanations are needed.

First, analyze the given conditions, then solve the problem step by step. Do not output the intermediate reasoning steps; directly output the final result."""

generate_request_prompt_template_old = \
"""[Original User Input]:
    {original_user_input}

[Current Task]:
    {current_task}

[API]
    {detail_app_api_description}

[Instructions]:
    1, Fill the api param that can answer the user's question;
    2, Output in the following format: {"name":"$name", "path": "$path", "method": "$method", "content_type": "$content_type", "body": "$body", "reason": "$reason"}. No other explanations are needed.

First, analyze the given conditions, then solve the problem step by step. Do not output the intermediate reasoning steps; directly output the final result."""

evaluate_prompt_template = \
"""
[Evaluated Api Path]:
    {evaluated_api_path}
    
[Evaluated Api Para]:
    {evaluated_api_para}
    
[Supplementary Parameters]
    {supplementary_parameters}

[All APIS of The System]:
{brief_api_description}

[Instructions]:
    1, Evaluate if the the api parameter is qualified;
    2, If you think the api parameter is qualified, output in format {"parameter_qualified": true, "parameter": {$parameter}, "reason": "$reason"} and fill the api parameter;
    3, If you think the api parameter is not qualified, output in format {"parameter_qualified": false, "reason": "$reason"}.

First, analyze the given conditions, then solve the problem step by step. Do not output the intermediate reasoning steps; directly output the final result."""


generate_plan_to_fullfill_api_prompt_template = \
"""[Target App Api]:
    {target_app_api_descriptions}

[User Input]
    {user_input}

[All APIS of The System]:
    {brief_api_description}

[Instructions]:
    1, Generate plans to make the Target App Api parameter qualified.
    2, You can call other api of the system or ask the user to provide.
    3, Prefer to ask other Apis than to ask user.
    4, Never ask the user to provide parameters with relatively poor readability.
    5, Output in the format [{"action_type": "$action_type", "api_path": "$api_path", "task": "The task the api should achieve or the information the user should provide."}, ...]. 
    The action type is either api_request or ask_user. Leave the api_path blank if the plan item is to ask user.

First, analyze the given conditions, then solve the problem step by step. Do not output the intermediate reasoning steps; directly output the final result."""

decode_result_prompt_template = \
"""[Task]:
    {task}

[Response Provider]:
    {response_provider}    

[Response]:
    {response}

[Instructions]:
    Extract information from the Response that can complete the task.     

First, analyze the given conditions, then solve the problem step by step. Do not output the intermediate reasoning steps; directly output the final result."""

class GeneralLlmAppAgent(BaseAgent):
    def __init__(self):
        self.memmory: Memmory = Memmory()
        super().__init__()
        self.max_recurrence_depth = 5
        self.current_recurrence_cnt = 1

    def init(self, agent_meta: AgentMeta, agent_config: AgentConfig, globals: Globals, io: BaseIo, system_config: SystemConfig) -> int:
        super().init(agent_meta, agent_config, globals, io, system_config)

        logger.debug("init suc")
        return 0

    def get_app_api_list_and_dict(self, app_id: str) -> (list, dict):
        path_2_app_api_dict = {}
        try:
            with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
                app_api_list: list[AppApi] = session.query(AppApi).filter(AppApi.app_id == app_id).all()

                for app_api in app_api_list:
                    path_2_app_api_dict[app_api.path] = app_api

            logger.debug("get_app_api_list suc")
            return app_api_list, path_2_app_api_dict
        except Exception as e:
            logger.error("catch exception:%s" % str(e))
            return [], {}

    def get_brief_app_api_descriptions(self, app_api_list: list[AppApi]) -> str:
        output_api_description = ""
        index = 0
        for app_api in app_api_list:
            select_api_description_item = \
"""    {api_index}:
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

    def get_brief_app_api_descriptions_v2(self, app_api_list: list[AppApi]) -> str:
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
                app_list: list[App] = session.query(App).filter(App.id == app_id).all()

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
    #
    # def process(self, message: Message) -> dict:
    #     return self._actually_process(message.person_input, message.person_input, message.app_id)

    def _get_supplementary_para_by_querying_api(self, path_2_app_api: dict, host: str, request_api_path: str,
                                                original_user_input: str, current_task: str):
        response = self._execute_api_request_by_api(path_2_app_api, host, request_api_path, original_user_input, current_task)
        return response

    def _get_supplementary_para_by_querying_user(self, query_user: str):
        return ""

    def _get_supplementary_para(self, llm_output_json: dict, path_2_app_api: str, host: str, original_user_input: str, current_task: str):
        request_api_path = llm_output_json.get("request_api", "")
        query_user = llm_output_json.get("query_user", "")

        if request_api_path != "":
            return self._get_supplementary_para_by_querying_api(path_2_app_api, host, request_api_path, original_user_input, current_task)
        elif query_user != "":
            return self._get_supplementary_para_by_querying_user(query_user)
        else:
            return ""

    def _execute_api_request_by_api(self, path_2_app_api: dict, host: str, path: str, historical_context: str, task: str):
        app_api = path_2_app_api[path]

        detail_app_api_description = self.get_detail_app_api_description(app_api)

        generate_request_prompt = generate_request_prompt_template.replace("{historical_context}", historical_context). \
            replace("{task}", task). \
            replace("{detail_app_api_description}", detail_app_api_description)

        llm_output = self.globals.general_llm_adapter.process(generate_request_prompt)
        generate_app_api = json.loads(llm_output)

        respose = make_http_request(host, generate_app_api["path"], generate_app_api["method"], \
                                    generate_app_api["content_type"], generate_app_api["body"])

        if len(task) > 0:
            decode_result_prompt = decode_result_prompt_template.replace("{task}", task)\
                                                                .replace("{response_provider}", path)\
                                                                .replace("{response}", json.dumps(respose))

            llm_output = self.globals.general_llm_adapter.process(decode_result_prompt)
            return llm_output
        else:
            return respose

    def _generate_historical_context(self, message: Message):
        pass

    def process(self, message: Message) -> dict:
    # def _actually_process(self, original_user_input: str, current_input: str, app_id: str) -> dict:
        app: App = self.get_app(message.app_id)
        if app is None:
            logger.error("process failed")
            return

### select api start
        app_api_list, path_2_app_api = self.get_app_api_list_and_dict(message.app_id)

        brief_app_api_descriptions = self.get_brief_app_api_descriptions(app_api_list)
        select_api_prompt = select_api_prompt_template.replace("{user_question}", message.person_input) \
                                                      .replace("{brief_api_description}", brief_app_api_descriptions)

        llm_output = self.globals.general_llm_adapter.process(select_api_prompt)
        selected_api = json.loads(llm_output)
        path = selected_api["path"]
        app_api = path_2_app_api[path]

        if path not in path_2_app_api:
            logger.error("could not find app_api relevant to the path:%s" % path)
            return

        generate_plan_to_full_file_api_prompt = generate_plan_to_fullfill_api_prompt_template\
                                                .replace("{target_app_api_descriptions}", self.get_detail_app_api_description(app_api)) \
                                                .replace("{user_input}", message.person_input) \
                                                .replace("{brief_api_description}", brief_app_api_descriptions)

        llm_output = self.globals.general_llm_adapter.process(generate_plan_to_full_file_api_prompt)
        llm_output_json = json.loads(llm_output)
        for plan_item in llm_output_json:
            action_type = plan_item["action_type"]
            if action_type == "api_request":
                api_path = plan_item["api_path"]
                task = plan_item["task"]
                result = self._execute_api_request_by_api(path_2_app_api, app.host, api_path, message.person_input, task)
                pass
            elif action_type == "query_user":
                pass
            ### select api end

### evaluate api qualified start
    #     evaluated_api_para = {}
    #     supplementary_para = {}
    #     while True:
    #         evaluate_prompt = evaluate_prompt_template.replace("{evaluated_api_path}", path).\
    #             replace("{evaluated_api_para}", json.dumps(evaluated_api_para)).\
    #             replace("{brief_api_description}", brief_app_api_descriptions).\
    #             replace("{supplementary_parameters}", json.dumps(supplementary_para))
    #
    #         llm_output = self.globals.general_llm_adapter.process(evaluate_prompt)
    #         llm_output_json = json.loads(llm_output)
    #         parameter_qualified = llm_output_json.get("parameter_qualified")
    #         if parameter_qualified is False:
    #             current_task = llm_output_json.get("current_task")
    #             supplementary_para = self._get_supplementary_para(llm_output_json, path_2_app_api, app.host, original_user_input, current_task)
    #             continue
    #         else:
    # ### evaluate api qualified end
    #             response = self._execute_api_request_by_api(path_2_app_api, app.host, path, original_user_input, "")
    #             # app_api = path_2_app_api[path]
    #             #
    #             # detail_app_api_description = self.get_detail_app_api_description(app_api)
    #             #
    #             # generate_request_prompt = generate_request_prompt_template.replace("{user_question}", current_input).\
    #             #                                  replace("{app_host}", app.host).\
    #             #                                  replace("{detail_app_api_description}", detail_app_api_description)
    #             #
    #             # llm_output = self.globals.general_llm_adapter.process(generate_request_prompt)
    #             # generate_app_api = json.loads(llm_output)
    #             #
    #             # respose = make_http_request(app.host, generate_app_api["path"], generate_app_api["method"], \
    #             #                             generate_app_api["content_type"], generate_app_api["body"])
    #
    #             logger.debug("App Agent process suc")
    #             return response

def make_http_request(host, url, method, content_type, body):
    import requests
    full_url = "%s/%s" % (host.rstrip("/"), url.lstrip("/"))
    headers = {'Content-Type': content_type}
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except Exception as e:
            logger.error("catch exception:%s" % str(e))
            logger.error("make_http_request failed")
            return ""

    response = requests.request(method, full_url, json=body, headers=headers)

    if response.status_code == 200:
        logger.debug("make_http_request suc, response:%s" % response.json())
        return response.json()
    else:
        logger.debug("make_http_request failed, response:%s" % response.text)
        return response.text
