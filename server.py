from flask import Flask, request
import json
from smooch import Smooch
import os
import adventure.loader as advent
import time
import logging
import sys
import smooch_parse as parse
import tip
import redis

s_api = Smooch(str(os.getenv("SMOOCH_KEY_ID")), str(os.getenv("SMOOCH_SECRET")))
r = redis.from_url(os.environ.get("REDIS_URL"))

app = Flask(__name__)

@app.route('/hooks',methods=['POST'])
def process_mesage():
    """Listens at /hooks for posts to that url."""

    data = json.loads(request.data.decode("utf-8"))

    try:
        user_response = parse.most_recent_msg(data)
        user_id = parse.get_user_id(data)
    except:
        logging.debug("PARSE FAILED={}".format(sys.exc_info()[0]))
        return

    logging.debug("user_id={0}, user_response={1}".format(user_id, user_response))

    if tip.is_tip(user_response.lower()):
        logging.debug("TIP TEXT={}".format(user_response))
        tip_amount = tip.tip_amount(user_response)
        s_api.post_message(user_id, "$[{0}]({1})".format("Confirm Tip", tip_amount), True)
        r.lpush("tip:" + user_id, tip_amount)
        return "OK"

    if advent.user_exists(user_id):
        logging.debug("PROCESSING RESPONSE FOR={}".format(user_id))
        response = advent.respond(user_id, user_response).strip()
    else:
        logging.debug("CREATING NEW USER={}".format(user_id))
        response = advent.new_game(user_id).strip()

    r.lpush("conv:" + user_id, user_response)
    r.lpush("conv:" + user_id, response)

    logging.debug("user={0} game reply={1}".format(user_id,response))
    s_api.post_message(user_id, response, True)
    return "OK"

@app.route('/')
def index():
    """Throws up HTML to index page to check if working properly"""
    return 'Welcome to Adventure'

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d  - %(message)s')
    s_api.delete_all_webhooks()
    webhook_id, webhook_secret = s_api.make_webhook("http://advent-term-120.herokuapp.com/hooks", "message:appUser")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
