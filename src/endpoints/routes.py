from aiohttp import web

from src.services.handlers import ping, set_value, get_value, publish_msg


def init_routes(app: web.Application) -> None:
    add_route = app.router.add_route
    add_route('get', '/redis_poc/ping', ping, name='ping')
    add_route('post', '/redis_poc/set_value', set_value, name='set_value')
    add_route('post', '/redis_poc/get_value', get_value, name='get_value')
    add_route('post', '/redis_poc/publish_message', publish_msg, name='publish_msg')
