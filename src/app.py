import asyncio
import inspect
import os
import platform
import sys

from aiohttp import web
from aiohttp_swagger import *

sys.path.append("./..")

from src.config_reader.config_module import ConfigModule
from src.endpoints.routes import init_routes
from src.loggingmodule.logging_module import LoggingModule, INFO, info_msg, ERROR, error_logging


try:
    config_obj = ConfigModule("common_config")
    logger_object = LoggingModule(name=os.path.basename(__file__).replace("py", ''),
                                  debug_level=int(config_obj.get_config_details("debug_level")))
except Exception as e:
    raise Exception("config_reading_error" + str(e))


def create_app():
    app = web.Application()
    init_routes(app)

    setup_swagger(
        app=app,
        swagger_url=f'/poc_docs',
        swagger_from_file='./endpoints/documentation.yaml'
    )
    return app


async def web_app():
    logger_object.log_message(INFO, info_msg(msg=('>>>>> Starting development server at http://{}/api/ <<<<<'
                                                  .format(platform.node())), source=inspect.currentframe())
                              )
    try:
        if platform.system() != 'Windows':
            import uvloop
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except:
        logger_object.log_message(ERROR, error_logging(sys.exc_info()))

    app = create_app()
    return app


if __name__ == '__main__':
    web.run_app(web_app(), host=config_obj.get_config_details("ip"), port=int(config_obj.get_config_details("port")))
