import datetime
import json
import logging
import sys

import smooch
from flask import Flask, request, render_template, redirect

from conn import r
from conv_mechanics import postback
from conv_mechanics import responder
from parse import smooch_parse as parse

app = Flask(__name__)


@app.template_filter()
def datetimefilter(value, format='%Y/%m/%d %H:%M'):
    """convert a datetime to a different format."""
    return value.strftime(format)


app.jinja_env.filters['datetimefilter'] = datetimefilter


@app.route('/yesno', methods=['POST'])
def process_postback():
    data = request.data.decode("utf-8")

    logging.info(data)

    request_data = json.loads(data)

    if not is_unique(request_data, parse.get_postback_id):
        return "", 200

    postback_payload = parse.get_postback_payload(request_data)
    user_id = parse.get_user_id(request_data)

    success = postback.process_postback(postback_payload, user_id)

    if success:
        logging.info("Successful response={}".format(user_id))
        return "", 200
    else:
        logging.error("Invalid Postback={} user={} data={}".format(postback_payload, user_id, request_data))


@app.route('/general', methods=['POST'])
def process_mesage():
    """Listens at /hooks for posts to that url and gets response from game engine."""

    data = request.data.decode("utf-8")

    logging.info(data)

    request_data = json.loads(data)

    if not is_unique(request_data, parse.get_message_id):
        return "", 200

    try:
        user_response = parse.most_recent_msg(request_data)
        user_id = parse.get_user_id(request_data)
    except:
        logging.error("PARSE FAILED={}".format(sys.exc_info()[0]))
        raise ParseException(sys.exc_info()[0])

    logging.info("user_id={0}, user_response={1}".format(user_id, user_response))

    logging.debug("restart status={}".format(r.get("restart:" + user_id)))

    success = responder.process_response(user_response, user_id)

    if success:
        logging.info("Successful response={}".format(user_id))
        return "", 200
    else:
        logging.error("Response Failure user_response={} user_id={}".format(user_response, user_id))


@app.route('/')
def index():
    """Throws up HTML to index page to check if working properly"""
    return redirect("https://devinmcgloin.com/advent/", code=302)


@app.route('/highscores')
def display_highscores():
    return render_template("highscores.html", title="Highscores", month=datetime.datetime.now(),
                           month_scores=[("Kevin K.", 105), ("Gerald G.", 98)],
                           all_time_scores=[("Jason J.", 243), ("Usain U.", 210)])


class ParseException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


@app.before_first_request
def setup():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d  - %(message)s',
                        stream=sys.stdout)

    try:
        smooch.delete_all_webhooks()
        smooch.create_webhook("https://advent.devinmcgloin.com/general", ["message:appUser"])
        smooch.create_webhook("https://advent.devinmcgloin.com/yesno", ["postback"])
    except:
        logging.error("Failed to create webhooks")


def is_unique(conversation, func):
    msg_id = func(conversation)
    if r.exists("msg:" + msg_id):
        return False
    else:
        r.set("msg:" + msg_id, True)
        return True


if __name__ == '__main__':
    app.run()
