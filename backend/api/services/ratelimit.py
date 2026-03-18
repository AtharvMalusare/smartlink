import redis
import time

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def is_rate_limited(ip: str, max_requests: int = 60, window: int = 60) -> bool:
    key = f"ratelimit:{ip}"
    now = time.time()
    window_start = now - window

    pipe = r.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)
    pipe.zadd(key, {str(now): now})
    pipe.zcard(key)
    pipe.expire(key, window)
    results = pipe.execute()

    request_count = results[2]
    return request_count > max_requests