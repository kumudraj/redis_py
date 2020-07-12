import inspect
import json
import os
import sys

from aiohttp.web_response import Response

from src.config_reader.config_module import ConfigModule
from src.loggingmodule.logging_module import LoggingModule, ERROR, error_logging, INFO, info_msg
from src.services.decorator_services import swagger_validation
from src.services.end_services import save_to_redis, get_data_with_key, redis_publish

config_obj = ConfigModule("common_config")
logger_object = LoggingModule(name=os.path.basename(__file__).replace("py", ''))


@swagger_validation
async def set_value(request):
    try:
        request_payload = await request.json()
        id = save_to_redis(request_payload)
        output = {'id': id}
        logger_object.log_message(INFO, info_msg(msg="Data save with id:{0}".format(id), source=inspect.currentframe()))
        return Response(body=json.dumps(output), status=200, content_type='application/json')
    except:
        logger_object.log_message(ERROR, error_logging(sys.exc_info()))
        return Response(body=json.dumps({"Error": 1}), status=200, content_type='application/json')


@swagger_validation
async def get_value(request):
    try:
        request_payload = await request.json()
        id = request_payload.get('id').strip()
        output = get_data_with_key(id)
        logger_object.log_message(INFO, info_msg(msg="result:{0}".format(output), source=inspect.currentframe()))
        return Response(body=json.dumps(output), status=200, content_type='application/json')

    except:
        logger_object.log_message(ERROR, error_logging(sys.exc_info()))
        return Response(body=json.dumps({"Error": 1}), status=200, content_type='application/json')


@swagger_validation
async def publish_msg(request):
    try:
        request_payload = await request.json()
        output = redis_publish(request_payload)
        # logger_object.log_message(INFO, info_msg(msg="result:{0}".format(output), source=inspect.currentframe()))
        return Response(body=json.dumps(output), status=200, content_type='application/json')

    except:
        logger_object.log_message(ERROR, error_logging(sys.exc_info()))
        return Response(body=json.dumps({"Error": 1}), status=200, content_type='application/json')


async def ping(request):
    try:
        return Response(body=json.dumps({"ping": 'ok'}), status=200, content_type='application/json')
    except:
        logger_object.log_message(ERROR, error_logging(sys.exc_info()))
        return Response(body=json.dumps({"ping": 'not_found'}), status=500, content_type='application/json')
