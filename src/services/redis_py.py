import inspect
import json
import os
import sys
import threading
import time

import redis
from ksuid import ksuid

from src.config_reader.config_module import ConfigModule
from src.loggingmodule.logging_module import LoggingModule, ERROR, error_logging, DEBUG, info_msg, INFO
from src.services.singleton import Singleton

config_obj = ConfigModule("common_config")
logger_object = LoggingModule(name=os.path.basename(__file__).replace("py", ''))

try:
    redis_host = 'localhost'
    redis_password = None
    redis_port = 6379
    redis_db = 1
except Exception as e:
    raise Exception(str(e))


def expiry_hrs(channel='default'):
    _hrs = int(1)
    return 10 if not _hrs else _hrs


def reload_channel():
    return 'dev'


@Singleton
class RPCServer:
    __slots__ = ('pool', 'redis_client', 'redis_subscribe', 'db')

    def __init__(self, db=None):
        if db:
            self.redis_client = redis.StrictRedis(connection_pool=self.get_redis_pool(db))
            self.redis_subscribe = self.get_redis_subscribe()
            self.db = db

    def get_redis_pool(self, r_db):
        try:
            print("########## Redis host: {0}, DB: {1} Channel: {2} connecting  ##########".format(
                redis_host, r_db, reload_channel()))
            if redis_password:
                pool = redis.ConnectionPool(host=redis_host, port=redis_port, db=r_db, encoding="utf-8",
                                            decode_responses=True, socket_timeout=120, retry_on_timeout=True,
                                            password=redis_password, health_check_interval=30, socket_read_size=65536)
            else:
                pool = redis.ConnectionPool(host=redis_host, port=redis_port, db=r_db, encoding="utf-8",
                                            decode_responses=True, socket_timeout=120, retry_on_timeout=True,
                                            health_check_interval=30, socket_read_size=65536)
            return pool
        except:
            logger_object.log_message(ERROR, error_logging(sys.exc_info()))

    def pool_reconnect(self):
        try:
            self.redis_client.connection_pool.disconnect()
        except:
            logger_object.log_message(ERROR, error_logging(sys.exc_info()))

        try:
            self.redis_client = redis.StrictRedis(connection_pool=self.get_redis_pool(self.db))
            self.redis_subscribe = self.get_redis_subscribe()
        except:
            logger_object.log_message(ERROR, error_logging(sys.exc_info()))

    def get_rerdis_connection(self):
        return redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

    def save_response_with_id(self, response, existing_id=None):
        try:
            if not existing_id:
                existing_id = str(ksuid())
            key_ttl = 60 * 60
            status = self.redis_client.set("{0}".format(existing_id), json.dumps(response))
            self.redis_client.expire("{0}".format(existing_id), key_ttl)
            return existing_id
        except redis.ConnectionError:
            logger_object.log_message(ERROR, error_logging(sys.exc_info()))
            self.redis_client = redis.StrictRedis(connection_pool=self.get_redis_pool(self.db))
        except:
            logger_object.log_message(ERROR, error_logging(sys.exc_info()))
            return None

    def get_response_with_id(self, response_id):
        try:
            response_data = self.redis_client.get("{0}".format(response_id))
            if response_data:
                response_data = json.loads(response_data)
                return response_data
            else:
                return {}
        except:
            logger_object.log_message(ERROR, error_logging(sys.exc_info()))

    def publish_message(self, pub_dict):
        try:
            start = time.time()
            self.redis_client.pubsub()
            self.redis_client.publish(reload_channel(), str("Ping"))
            done = time.time()
            publish_duration = done - start
            if (publish_duration) > 7:
                logger_object.log_message(DEBUG,
                                          info_msg(msg="publish_duration:{0} sec.".format(publish_duration),
                                                   source=inspect.currentframe()))
                self.pool_reconnect()
            self.redis_client.pubsub()
            self.redis_client.publish(reload_channel(), str(pub_dict))
            logger_object.log_message(INFO,
                                      info_msg(msg="publish msg:{0}".format(pub_dict),
                                               source=inspect.currentframe()))
            return True
        except:
            logger_object.log_message(ERROR, error_logging(sys.exc_info()))
            return False

    def get_redis_subscribe(self):
        try:
            while True:
                try:
                    redis_process = self.redis_client.pubsub(ignore_subscribe_messages=True)
                    redis_process.subscribe(reload_channel())
                    if redis_process:
                        break
                except:
                    logger_object.log_message(ERROR, error_logging(sys.exc_info()))
            return redis_process
        except:
            logger_object.log_message(ERROR, error_logging(sys.exc_info()))

    def get_redis_message(self):
        try:
            if not self.redis_subscribe:  #### after restart redis manually, self.redis_subscribe was null  error recived {'Type': 'AttributeError', 'Msg': AttributeError("'NoneType' object has no attribute 'get_message'")
                self.redis_subscribe = self.get_redis_subscribe()
            self.redis_subscribe.check_health()
            health_check_response = ", ".join(self.redis_subscribe.health_check_response)
            # logger_object.log_message(DEBUG,
            #                           info_msg(msg="pub_sub health:{0}".format(health_check_response),
            #                                    source=inspect.currentframe()))
            return self.redis_subscribe.get_message()
        except redis.ConnectionError:
            logger_object.log_message(ERROR, error_logging(sys.exc_info()))
            self.redis_client = redis.StrictRedis(connection_pool=self.get_redis_pool(self.db))
            self.redis_subscribe = self.get_redis_subscribe()
        except:
            logger_object.log_message(ERROR, error_logging(sys.exc_info()))

    def remove_key(self, key):
        try:
            if isinstance(key, str):
                self.redis_client.delete(key)
            else:
                self.redis_client.delete(*key)
        except redis.ConnectionError:
            logger_object.log_message(ERROR, error_logging(sys.exc_info()))
            self.redis_client = redis.StrictRedis(connection_pool=self.get_redis_pool(self.db))
        except:
            logger_object.log_message(ERROR, error_logging(sys.exc_info()))


@Singleton
class Queue:
    __slots__ = 'items'

    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.insert(0, item)

    def dequeue(self):
        try:
            if self.size > 0:
                return self.items.pop()
        except:
            logger_object.log_message(ERROR, error_logging(sys.exc_info()))

    @property
    def size(self):
        return len(self.items)


queue_obj = Queue()
redis_obj = RPCServer(redis_db)


def create_redis_msg_queue():
    try:
        message = redis_obj.get_redis_message()
        if message and message.get('data') != 'Ping':
            print("got message:", message.get('data'))
            message = json.loads(message.get("data").replace('\'', '"'))
            queue_obj.enqueue(message)
    except:
        logger_object.log_message(ERROR, error_logging(sys.exc_info()))
    finally:
        threading.Timer(2.0, create_redis_msg_queue).start()


create_redis_msg_queue()
