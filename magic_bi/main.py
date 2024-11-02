from signal import signal, SIGINT

from loguru import logger
import argparse

from magic_bi.utils.utils import init_log
from magic_bi.utils.init_orm_entity import init_entity
from magic_bi.offline_main import offline_main
from magic_bi.online_main import online_main
from magic_bi.utils.globals import GLOBALS, GLOBAL_CONFIG

def exit_func(signal_received, frame):
    print("Magic-Data exit")
    exit(0)

def init_arg():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--operating_mode', type=str, help='support modes: online, offline')
    arg_parser.add_argument('--config', type=str, help='config file path', default="config/system.yml")
    args = arg_parser.parse_args()

    logger.debug("init_arg suc")
    return args

if __name__ == '__main__':
    signal(SIGINT, exit_func)
    init_log()
    init_entity()
    args = init_arg()

    ret = GLOBAL_CONFIG.parse(config_file_path=args.config)
    if ret != 0:
        logger.error("init global config failed")
        exit(-1)

    ret = GLOBALS.init(global_config=GLOBAL_CONFIG)
    if ret != 0:
        logger.error("init globals failed")
        exit(-1)

    if args.operating_mode == 'online':
        online_main()
    elif args.operating_mode == 'offline':
        offline_main()
    else:
        exit(-1)
