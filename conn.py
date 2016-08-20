import os

import redis

r = redis.from_url(os.getenv("REDIS_URL", 'redis://localhost:6379'))
