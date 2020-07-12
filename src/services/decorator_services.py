import functools
import json
import os
import sys
from functools import wraps

from aiohttp.web_response import Response

from src.config_reader.config_module import ConfigModule
from src.loggingmodule.logging_module import LoggingModule

bot_cache_dict = dict()

config_obj = ConfigModule("common_config")
logger_object = LoggingModule(name=os.path.basename(__file__).replace("py", ''))


def func_omission(func):
    @wraps(func)
    def omission_logger(*args, **kwargs):
        try:
            value = func(*args, **kwargs)
            return value
        except:
            print(sys.exc_info())
            return None

    return omission_logger


def swagger_validation(func):
    @functools.wraps(func)
    def wrapper(*args):
        request = args[0]
        if "referer" in request.headers and "faq_builder_docs" in request.headers.get("referer"):
            if "swagger_auth" in request.headers:
                key = request.headers["swagger_auth"]
                if key != config_obj.get_config_details("secret_key"):
                    return Response(body=json.dumps({"message": "unauthorized access"}),
                                    status=200, content_type='application/json')
            else:
                return Response(body=json.dumps({"message": "unauthorized access"}),
                                status=200, content_type='application/json')
        value = func(*args)
        return value

    return wrapper
