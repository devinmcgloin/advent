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

    request_data = json.loads(request.data.decode("utf-8"))

    logging.info(request_data)

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

    logging.debug("user={0} game reply={1}".format(user_id,response))

    schedule = schedule_msg(response)

    t = time.time()
    for msg in schedule:
        t = int(t + msg[1])
        pq.add_task((user_id, msg[0]), t)


    q.enqueue_call(func=respond, args=(pq,))

    pq = PriorityQueue()

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
