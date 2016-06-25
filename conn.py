import os

import redis
from rq import Queue

r = redis.from_url(os.getenv("REDIS_URL", 'redis://localhost:6379'))
q = Queue("default", connection=r)
