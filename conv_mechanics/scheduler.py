import logging
import random as random
import re
import time

import smooch

from datastructures.pq import PriorityQueue


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
        return [(msg[0], 0)]
    else:
        order = []
        next_fast = False
        for i, sentence in enumerate(msg):
            if i == 0:
                order.append((sentence, 0))
            elif next_fast:
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
