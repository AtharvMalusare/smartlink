import redis
import json

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def get_cached_link(short_code: str):
    data = r.get(f"link:{short_code}")
    if data:
        return json.loads(data)
    return None

def cache_link(short_code: str, data: dict, ttl: int = 3600):
    r.setex(f"link:{short_code}", ttl, json.dumps(data))

def invalidate_link(short_code: str):
    r.delete(f"link:{short_code}")