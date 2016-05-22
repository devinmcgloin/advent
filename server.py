from flask import Flask, request
import json
from pysmooch.smooch import Smooch
import os
import time
import logging
import sys
import redis
from rq import Queue
from rq.job import Job
from worker import respond
import pysmooch.smooch_parse as parse
import adventure.loader as advent
import tip
import re
import random
from pq import PriorityQueue

pq = PriorityQueue()

s_api = Smooch(str(os.getenv("SMOOCH_KEY_ID")), str(os.getenv("SMOOCH_SECRET")))
r = redis.from_url(os.getenv("REDIS_URL", 'redis://localhost:6379'))
logging.debug(os.getenv("REDIS_URL", 'redis://localhost:6379'))
q = Queue("default", connection=r)

app = Flask(__name__)

@app.route('/hooks',methods=['POST'])
def process_mesage():
    """Listens at /hooks for posts to that url."""

    data = request.data.decode("utf-8")

    logging.info(data)

    q.enqueue_call(func=respond, args=(data,))


    logging.debug("JOB SENT")

    return "OK"

@app.route('/')
def index():
    """Throws up HTML to index page to check if working properly"""
    return 'Welcome to Adventure'

class ParseException(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

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

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d  - %(message)s')
    s_api.delete_all_webhooks()
    webhook_id, webhook_secret = s_api.make_webhook("http://advent-term-120.herokuapp.com/hooks", "message:appUser")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
