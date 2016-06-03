import logging
import random as random
import re
import time

import smooch

from datastructures.pq import PriorityQueue


def respond(user_id, response):
    for msg in response.split("\n"):
        smooch.send_message(user_id, msg)
        time.sleep(1)
