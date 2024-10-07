import uvicorn
from signal import signal, SIGINT
from loguru import logger
import argparse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from magic_bi.utils.utils import init_log
from magic_bi.utils.globals import GLOBAL_CONFIG, GLOBALS
from magic_bi.utils.init_orm_entity import init_entity
from magic_bi.web.agent_router import create_agent_router
from magic_bi.web.data_connector_router import create_data_connector_router
from magic_bi.web.data_router import create_data_router
from magic_bi.web.recommend_router import create_recommend_router
from magic_bi.web.user_router import create_user_router
from magic_bi.web.dataset_router import create_dataset_router
from magic_bi.web.app_router import create_app_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 可以指定特定的域名，例如 ["http://example.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def exit_func(signal_received, frame):
    print("Magic-Data exit")
    exit(0)

def init_arg():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--start_mode', type=str, help='support modes: mq, web')
    arg_parser.add_argument('--config', type=str, help='config file path', default="config/magic_bi_local.yml")
    args = arg_parser.parse_args()

    logger.debug("init_arg suc")
    return args

def test_func():
    pass

def main():
    init_entity()

    signal(SIGINT, exit_func)
    init_log()
    args = init_arg()

    ret = GLOBAL_CONFIG.parse(config_file_path=args.config)
    if ret != 0:
        logger.error("init global config failed")
        exit(-1)

    ret = GLOBALS.init(global_config=GLOBAL_CONFIG)
    if ret != 0:
        logger.error("init globals failed")
        exit(-1)

    from magic_bi.mq.mq_process import init_mq_process


    if GLOBAL_CONFIG.rabbitmq_config.loaded is True:
        init_mq_process(rabbitmq_config=GLOBAL_CONFIG.rabbitmq_config, func_callback=test_func)

    app.include_router(create_agent_router(GLOBAL_CONFIG.web_config.url_prefix))
    app.include_router(create_data_connector_router(GLOBAL_CONFIG.web_config.url_prefix))
    app.include_router(create_data_router(GLOBAL_CONFIG.web_config.url_prefix))
    app.include_router(create_dataset_router(GLOBAL_CONFIG.web_config.url_prefix))
    app.include_router(create_recommend_router(GLOBAL_CONFIG.web_config.url_prefix))
    app.include_router(create_user_router(GLOBAL_CONFIG.web_config.url_prefix))
    app.include_router(create_app_router(GLOBAL_CONFIG.web_config.url_prefix))

    uvicorn.run(app, port=GLOBAL_CONFIG.web_config.port, host="0.0.0.0")

if __name__ == '__main__':
    main()
