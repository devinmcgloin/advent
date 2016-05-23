import json
import logging
import os
import re
import sys
from datetime import datetime

import redis
from flask import Flask, request
from rq import Queue

import adventure.loader as advent
import pysmooch.smooch_parse as parse
import tip
from pysmooch.smooch import Smooch
from worker import respond
import highscore as hs

s_api = Smooch(str(os.getenv("SMOOCH_KEY_ID")), str(os.getenv("SMOOCH_SECRET")))
r = redis.from_url(os.getenv("REDIS_URL", 'redis://localhost:6379'))
q = Queue("default", connection=r)

app = Flask(__name__)


@app.route('/hooks', methods=['POST'])
def process_mesage():
    """Listens at /hooks for posts to that url and gets response from game engine."""

    data = request.data.decode("utf-8")

    logging.info(data)

    request_data = json.loads(data)
    try:
        user_response = parse.most_recent_msg(request_data)
        user_id = parse.get_user_id(request_data)
    except:
        logging.debug("PARSE FAILED={}".format(sys.exc_info()[0]))
        raise ParseException(sys.exc_info()[0])

    logging.info("user_id={0}, user_response={1}".format(user_id, user_response))

    logging.debug("restart status={}".format(r.get("restart:" + user_id)))

    user_exists = advent.user_exists(user_id)

    if user_exists and r.get("restart:" + user_id) == b'1':
        logging.debug("restart check for user={}".format(user_id))
        if re.search(user_response.strip().lower(), "^(yes|y)$"):
            response = advent.new_game(user_id)
            s_api.post_message(user_id, response, True)
            r.set("restart:" + user_id, 0)
        elif re.search(user_response.strip().lower(), "^(no|n)$"):
            r.set("restart:" + user_id, 0)
            s_api.post_message(user_id, "Ok", True)
        else:
            s_api.post_message(user_id, "Please answer the question.", True)
        return "OK"
    elif user_exists and r.get("highscore:" + user_id) == b'1':
        if re.search(user_response.strip().lower(), "^(yes|y)$"):
            response = hs.add_user_scoreboard(user_id, 1)
            s_api.post_message(user_id, response, True)
            r.set("highscore:" + user_id, 0)
        elif re.search(user_response.strip().lower(), "^(no|n)$"):
            r.set("highscore:" + user_id, 0)
            s_api.post_message(user_id, "Ok. \nYou can type 'restart' to play again.", True)
        else:
            s_api.post_message(user_id, "Please answer the question.", True)
        return "OK"
    elif tip.is_tip(user_response.lower()):
        logging.info("TIP TEXT={}".format(user_response))
        tip_amount = tip.tip_amount(user_response)

        # Smooch deals in terms of cents, so dollar amounts have to be converted
        tip_amount_adj = 100 * tip_amount
        s_api.post_buy_message(user_id, "Thank you for supporting Colossal Cave Adventures",
                               "Confirm Tip for {:.2f}".format(tip_amount), tip_amount_adj)
        logging.info("{1} tip from {0}".format(user_id, tip_amount))
        r.lpush("tip:" + user_id, tip_amount)
        return "OK"
    elif user_exists and (user_response.lower() == "restart" or user_response.lower() == "reset"):
        r.set("restart:" + user_id, 1)
        s_api.post_message(user_id, "Do you want to restart?\n I cannot undo this.", True)
        return "OK"
    elif user_response.lower() == "top score" or user_response.lower() == "high score":
        s_api.post_message(user_id, hs.get_top_ten(), True)
        return "OK"
    elif user_exists:
        logging.info("PROCESSING RESPONSE FOR={}".format(user_id))
        response = advent.respond(user_id, user_response).strip()
        if re.search("You scored \d+ out of a possible \d+ using \d+ turns.", response) \
                and hs.is_highscore(hs.get_score(response)):
            response += "\nWould you like to add your first name and last initial to the global high score list?"
            r.zadd("highscore:" + user_id, str(datetime.now()), hs.get_score(response))
    else:
        logging.info("CREATING NEW USER={}".format(user_id))
        response = advent.new_game(user_id).strip()

    r.rpush("conv:" + user_id, user_response)
    r.rpush("conv:" + user_id, response)

    logging.debug("user={0} game reply={1}".format(user_id, response))

    q.enqueue_call(func=respond, args=(user_id, response))

    logging.debug("JOB SENT")

    return "OK"


@app.route('/')
def index():
    """Throws up HTML to index page to check if working properly"""
    return 'Welcome to Adventure'


class ParseException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d  - %(message)s')
    s_api.delete_all_webhooks()
    webhook_id, webhook_secret = s_api.make_webhook("http://advent-term-120.herokuapp.com/hooks", "message:appUser")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
