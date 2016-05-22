import os
import sys

import redis
from rq import Worker, Queue, Connection

import logging
import json
import re

import time
import random as random




s_api = Smooch(str(os.getenv("SMOOCH_KEY_ID")), str(os.getenv("SMOOCH_SECRET")))
r = redis.from_url(os.getenv("REDIS_URL", 'redis://localhost:6379'))

listen = ["default"]



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d  - %(message)s')
    with Connection(r):
        logging.debug(listen)
        worker = Worker(listen)
        worker.work()

def respond(pq):
    while pq.length() > 0:
        if pq.priority() < time.time():
            logging.debug(pq.pop_task())
            s_api.post_message(task[0], task[1], True)
