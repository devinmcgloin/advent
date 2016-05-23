import logging
import os
import random as random
import re
import time

import redis
from rq import Worker, Connection

from pq import PriorityQueue
import smooch

r = redis.from_url(os.getenv("REDIS_URL", 'redis://localhost:6379'))

listen = ["default"]

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d  - %(message)s')
    with Connection(r):
        logging.debug(listen)
        worker = Worker(listen)
        worker.work()


def respond(user_id, response):
    schedule = schedule_msg(response)
    pq = PriorityQueue()

    t = time.time()
    for msg in schedule:
        t = int(t + msg[1])
        pq.add_task((user_id, msg[0]), t)

    while pq.length() > 0:
        if pq.lowest_priority() < time.time():
            task = pq.pop_task()
            logging.debug(task)
            if task[1]:
                smooch.send_message(task[0], task[1], True)


def schedule_msg(response):
    logging.info(response)
    SLOW = 10
    NORMAL = 6
    FAST = 3
    SUPER_FAST = 1
    msg = response.split("\n")
    if len(msg) == 1:
        return [(msg[0], random.randrange(NORMAL))]
    else:
        order = []
        next_fast = False
        for sentence in msg:
            if next_fast:
                order.append((sentence, random.randrange(SUPER_FAST)))
                next_fast = False
            elif len(sentence) < 40:
                order.append((sentence, random.randrange(SUPER_FAST)))
            elif len(sentence) > 140:
                order.append((sentence, random.randrange(NORMAL, SLOW)))
            elif re.search("(\?|\.)$", sentence):
                order.append((sentence, random.randrange(NORMAL)))
            elif re.search("\!+$", sentence):
                order.append((sentence, random.randrange(SUPER_FAST)))
            elif re.search("\!$", sentence):
                order.append((sentence, random.randrange(FAST)))
            elif re.search("\.+$", sentence):
                order.append((sentence, random.randrange(NORMAL)))
                next_fast = True
        return tuple(order)
