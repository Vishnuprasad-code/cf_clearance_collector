import json
import uuid

import redis


def get_uuid():
    uuid_ = str(uuid.uuid1()).replace("-", "")
    return uuid_


def connect_redis():
    return redis.Redis(host="local-redis-service",
                       port=6379, db=15, decode_responses=True)


def initialize_redis(uuid_):
    cli = connect_redis()
    cookies = {"state": "Processing", "cookies": {}, "error": None}
    cli.set(uuid_, json.dumps(cookies))
    return True


def set_cookies(uuid_, state=None, cookies=None, error=None):
    cli = connect_redis()
    cookies = {"state": "Finished", "cookies": cookies, "error": error}
    cli.set(uuid_, json.dumps(cookies))
    return True


def fetch_cookies(uuid_):
    cli = connect_redis()
    cookies = cli.get(uuid_)
    if not cookies:
        return {"state": "Finished", "cookies": {}, "error": "Invalid Task ID"}

    cookies = json.loads(cookies)
    return cookies


def clear_redis_key(uuid_):
    cli = connect_redis()
    del cli[uuid_]
