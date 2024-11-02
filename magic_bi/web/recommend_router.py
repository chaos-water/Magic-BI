from loguru import logger
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse


from magic_bi.utils.globals import GLOBALS, GLOBAL_CONFIG
from magic_bi.utils.utils import get_http_rsp
from magic_bi.message.message import Message
from magic_bi.recommend.recommender import Recommender
from magic_bi.recommend.user_portrait import UserPortrait

recommend_router = APIRouter()
# AGENT_MANAGER = AgentManager(global_config=GLOBAL_CONFIG, globals=GLOBALS)
RECOMMENDR = Recommender()
RECOMMENDR.init(GLOBALS)

USER_PORTRAIT = UserPortrait()
USER_PORTRAIT.init(GLOBALS)

# url_prefix = "magic_bi"
url_prefix = GLOBAL_CONFIG.system_config.url_prefix

def create_recommend_router(prefix: str):
    recommend_router = APIRouter(prefix=prefix)
    @recommend_router.options("/{path:path}")
    async def preflight_handler(request: Request):
        response = JSONResponse(content="")
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    @recommend_router.post("/%s/recommend/zero" % url_prefix)
    def zero_recommend(request: Request ,body: dict):
        recommendation_list = []
        user_id = request.headers.get("user_id", "default")
        
        data_source_id = body.get("data_source_id", "")
        dataset_id = body.get("dataset_id", "")
        data_id = body.get("data_id", "")
        count = body.get("count", 10)

        if (len(data_source_id) == 0 and len(dataset_id) == 0) or (len(data_source_id) > 0 and len(dataset_id) > 0) or count <= 0:
            logger.error("zero_recommend failed, body:%s" % body )
            return get_http_rsp(data=recommendation_list)

        recommendation_list = RECOMMENDR.zero_recommend(user_id, data_source_id, dataset_id, data_id, count)

        logger.debug("zero_recommend suc, user_id:%s, data_source:%s" % (user_id, data_source_id))
        return get_http_rsp(data=recommendation_list)

    @recommend_router.post("/%s/recommend/relevant" % url_prefix)
    def relevant_recommend(request: Request, body: dict):
        user_id = request.headers.get("user_id", "default")
        
        data_source_id = body.get("data_source_id")
        dataset_id = body.get("dataset_id")
        data_id = body.get("data_id")
        previous_person_input = body.get("previous_person_input")

        recommendation_list = RECOMMENDR.relevant_recommend(user_id, previous_person_input, data_source_id, dataset_id, data_id)

        logger.debug("relevant_recommend suc, user_id:%s, data_source_id:%s, dataset_id:%s, data_id:%s"
                     % (user_id, data_source_id, dataset_id, data_id))
        return get_http_rsp(data=recommendation_list)

    @recommend_router.post("/%s/recommend/personalization" % url_prefix)
    def relevant_recommend(request: Request, body: dict):
        user_id = request.headers.get("user_id", "default")
        
        user_portrait = USER_PORTRAIT.get_user_portrait(user_id)

        logger.debug("relevant_recommend suc")
        return get_http_rsp(data={"user_portrait": user_portrait})

    @recommend_router.post("/recommend/add_message")
    def relevant_recommend(body: dict):
        message: Message = Message()
        message.from_dict(body)
        from sqlalchemy.orm.session import Session
        with Session(GLOBALS.sql_orm.engine, expire_on_commit=False) as session:
            session.add(message)
            session.commit()

        logger.debug("add_message suc, body:%s" % body)
        return get_http_rsp()

    return recommend_router