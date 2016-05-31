import json
import logging
import os
import re
import sys

import smooch
from flask import Flask, request, render_template, redirect

from adventure import advent
from conn import r, q
from conv_mechanics import tip
from conv_mechanics.scheduler import respond
from conv_mechanics import postback
from conv_mechanics import responder
from parse import smooch_parse as parse

app = Flask(__name__)


@app.route('/yesno', methods=['POST'])
def process_postback():
    data = request.data.decode("utf-8")

    logging.info(data)

    request_data = json.loads(data)

    postback_payload = parse.get_postback_payload(request_data)
    user_id = parse.get_user_id(request_data)

    success = postback.process_postback(postback_payload, user_id)

    if success:
        return "OK"
    else:
        logging.error("Invalid Postback={} user={} data={}".format(postback_payload, user_id, request_data))


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

    success = responder.process_response(user_response, user_id)

    if success:
        return "OK"
    else:
        logging.error("Response Failure user_response={} user_id={}".format(user_response, user_id))


@app.route('/')
def index():
    """Throws up HTML to index page to check if working properly"""
    return redirect("https://devinmcgloin.com/advent/", code=302)


@app.route('/highscores')
def display_highscores():
    return render_template("highscores.html", title="Highscores")

class ParseException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d  - %(message)s')
    #smooch.delete_all_webhooks()
    #smooch.create_webhook("http://advent-term-120.herokuapp.com/general", ["message:appUser"])
    #smooch.create_webhook("http://advent-term-120.herokuapp.com/yesno", ["postback"])
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
