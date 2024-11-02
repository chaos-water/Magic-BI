import uvicorn
from loguru import logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from magic_bi.utils.globals import GLOBAL_CONFIG, GLOBALS
from magic_bi.web.agent_router import create_agent_router
from magic_bi.web.data_source_router import create_data_source_router
from magic_bi.web.data_router import create_data_router
from magic_bi.web.recommend_router import create_recommend_router
from magic_bi.web.user_router import create_user_router
from magic_bi.web.dataset_router import create_dataset_router
from magic_bi.web.app_router import create_app_router
from magic_bi.web.train_data_router import create_train_data_router
from magic_bi.web.train_qa_file_router import create_train_qa_file_router
from magic_bi.web.model_router import create_train_model_router
from magic_bi.work.provided_work import register_work

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 可以指定特定的域名，例如 ["http://example.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def online_main():
    register_work()
    url_prefix = f"/{GLOBAL_CONFIG.system_config.url_prefix}"
    app.include_router(create_agent_router(url_prefix))
    app.include_router(create_data_source_router(url_prefix))
    app.include_router(create_data_router(url_prefix))
    app.include_router(create_dataset_router(url_prefix))
    app.include_router(create_recommend_router(url_prefix))
    app.include_router(create_user_router(url_prefix))
    app.include_router(create_app_router(url_prefix))
    app.include_router(create_train_data_router(url_prefix))
    app.include_router(create_train_qa_file_router(url_prefix))
    app.include_router(create_train_model_router(url_prefix))

    uvicorn.run(app, port=GLOBAL_CONFIG.system_config.port, host="0.0.0.0")
