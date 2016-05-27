import datetime
import json
import logging
import os
import re
import sys

import redis
from flask import Flask, request
from rq import Queue

import adventure.loader as advent
import highscore as hs
import smooch_parse as parse
import tip
import smooch
from worker import respond

r = redis.from_url(os.getenv("REDIS_URL", 'redis://localhost:6379'))
q = Queue("default", connection=r)

app = Flask(__name__)


@app.route('/yesno', methods=['POST'])
def process_postback():

    data = request.data.decode("utf-8")

    logging.info(data)

    request_data = json.loads(data)

    postback_payload = parse.get_postback_payload(request_data)
    user_id = parse.get_user_id(request_data)

    if not r.get("yesno:"+user_id):
        return "OK"

    if postback_payload.startswith("restart"):
        if postback_payload.endswith("yes"):
            advent.new_game(user_id)
            response = advent.respond(user_id, "no")
            smooch.send_message(user_id, response, True)
            r.delete("yesno:" + user_id)
        else:
            r.delete("yesno:" + user_id)
            smooch.send_message(user_id, "Ok.", True)
        return "OK"

    elif postback_payload.startswith("start_new"):
        if postback_payload.endswith("yes"):
            advent.new_game(user_id)
            response = advent.respond(user_id, "no")
            smooch.send_message(user_id, response, True)
            r.delete("yesno:" + user_id)
        else:
            r.delete("yesno:" + user_id)
            r.delete("save:" + user_id)
            smooch.send_message(user_id, "Ok.", True)
        return "OK"

    elif re.match("(yes|no)", postback_payload):
        if postback_payload.endswith("yes"):
            response = advent.respond(user_id, "yes")

            # Checking if user has asked to end the game.
            if re.search("You scored \d+ out of a possible \d+ using \d+ turns.", response):
                respond(user_id, response)
                advent.new_game(user_id)
                r.set("yesno:" + user_id, "new_game")
                smooch.send_postbacks(user_id, "Do you want to play again?",
                                  {"Yes": "start_new_yes",
                                   "No": "start_new_no"})
                return "OK"
            smooch.send_message(user_id, response, True)
            r.delete("yesno:" + user_id)
        else:
            response = advent.respond(user_id, "no")
            smooch.send_message(user_id, response, True)
            r.delete("yesno:" + user_id)
        return "OK"


@app.route('/general', methods=['POST'])
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

    if r.get("yesno:"+user_id):
        response_type = r.get("yesno:"+user_id)
        logging.debug("Response type={}".format(response_type))
        if response_type == b'restart':
            smooch.send_postbacks(user_id, "Do you want to restart?",
                                  {"Yes": "yes",
                                   "No": "no"})
        elif response_type == b'new_game':
            smooch.send_postbacks(user_id, "Do you want to play again?",
                                  {"Yes": "yes",
                                   "No": "no"})
        elif response_type == b'game':
            smooch.send_postbacks(user_id, "Please answer the question.",
                                  {"Yes": "yes",
                                   "No": "no"})
        else:
            logging.debug("Extraneous response type={}".format(response_type))
        return "OK"

    elif tip.is_tip(user_response.lower()):
        logging.info("TIP TEXT={}".format(user_response))
        tip_amount = tip.tip_amount(user_response)

        # Smooch deals in terms of cents, so dollar amounts have to be converted
        tip_amount_adj = 100 * tip_amount
        smooch.request_payment(user_id, "Thank you for supporting Adventure",
                               {"Confirm Tip for {:.2f}".format(tip_amount): tip_amount_adj})
        logging.info("{1} tip from {0}".format(user_id, tip_amount))
        r.lpush("tip:" + user_id, tip_amount)
        return "OK"

    elif user_exists and (user_response.lower() == "restart" or user_response.lower() == "reset"):
        r.set("yesno:" + user_id, "restart")
        smooch.send_postbacks(user_id, "Do you want to restart?\n I cannot undo this.",
                              {"Yes": "restart_yes",
                               "No" : "restart_no"})
        return "OK"
    
    elif user_exists:
        response = advent.respond(user_id, user_response).strip()
        logging.info("user={0} game reply={1}".format(user_id, response))
        if advent.yes_no_question(user_id):
            split_response = response.split("\n")
            question = split_response[-1]
            del split_response[-1]
            respond(user_id, "\n".join(split_response))
            smooch.send_postbacks(user_id, question,
                                  {"Yes": "yes",
                                   "No": "no"})
            r.set("yesno:" + user_id, "game")
            return "OK"

        elif re.search("You scored \d+ out of a possible \d+ using \d+ turns.", response):
            respond(user_id, response)
            advent.new_game(user_id)
            r.set("yesno:"+user_id, "new_game")
            smooch.send_postbacks(user_id, "Do you want to play again?",
                                  {"Yes": "start_new_yes",
                                   "No": "start_new_no"})
            return "OK"
        else:
            logging.debug("user={0} game reply={1}".format(user_id, response))

            q.enqueue_call(func=respond, args=(user_id, response))
            return "OK"

    else:
        logging.info("CREATING NEW USER={}".format(user_id))
        response = advent.new_game(user_id).strip()
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
    smooch.delete_all_webhooks()
    smooch.create_webhook("http://advent-term-120.herokuapp.com/general", ["message:appUser"])
    smooch.create_webhook("http://advent-term-120.herokuapp.com/yesno", ["postback"])
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
