import sys
import time

import json
import logging
import os
import random as random
import re
import redis
from rq import Worker, Connection

import adventure.loader as advent
import pysmooch.smooch_parse as parse
import tip
from pysmooch.smooch import Smooch
from pq import PriorityQueue

s_api = Smooch(str(os.getenv("SMOOCH_KEY_ID")), str(os.getenv("SMOOCH_SECRET")))
r = redis.from_url(os.getenv("REDIS_URL", 'redis://localhost:6379'))

listen = ["default"]

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d  - %(message)s')
    with Connection(r):
        logging.debug(listen)
        worker = Worker(listen)
        worker.work()


def respond(data):
    request_data = json.loads(data)
    try:
        user_response = parse.most_recent_msg(request_data)
        user_id = parse.get_user_id(request_data)
    except:
        logging.debug("PARSE FAILED={}".format(sys.exc_info()[0]))
        raise ParseException(sys.exc_info()[0])

    logging.info("user_id={0}, user_response={1}".format(user_id, user_response))

    if tip.is_tip(user_response.lower()):
        logging.info("TIP TEXT={}".format(user_response))
        tip_amount = tip.tip_amount(user_response)
        s_api.post_message(user_id, "$[{}]({:.2f})".format("Confirm Tip", tip_amount), True)
        logging.info("$[{}]({:.2f})".format("Confirm Tip", tip_amount))
        r.lpush("tip:" + user_id, tip_amount)
        return "OK"

    if advent.user_exists(user_id):
        logging.info("PROCESSING RESPONSE FOR={}".format(user_id))
        response = advent.respond(user_id, user_response).strip()
    else:
        logging.info("CREATING NEW USER={}".format(user_id))
        response = advent.new_game(user_id).strip()

    r.rpush("conv:" + user_id, user_response)
    r.rpush("conv:" + user_id, response)

    logging.debug("user={0} game reply={1}".format(user_id, response))

    schedule = schedule_msg(response)
    pq = PriorityQueue()

    t = time.time()
    for msg in schedule:
        t = int(t + msg[1])
        pq.add_task((user_id, msg[0]), t)

    while pq.length() > 0:
        if pq.priority() < time.time():
            task = pq.pop_task()
            logging.debug(task)
            s_api.post_message(task[0], task[1], True)


def schedule_msg(response):
    logging.info(response)
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


class ParseException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
