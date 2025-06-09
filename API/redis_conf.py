import redis
from apscheduler.jobstores.redis import RedisJobStore

r = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

jobstore = RedisJobStore(
    host='localhost',
    port=6379,
    db=1
)



