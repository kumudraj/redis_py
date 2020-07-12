
from src.services.redis_py import redis_obj

def save_to_redis(data):
    return redis_obj.save_response_with_id(data)


def get_data_with_key(key):
    return redis_obj.get_response_with_id(key)

def redis_publish(message):
    return redis_obj.publish_message(message)