import os
import sys

import redis
from rq import Worker, Queue, Connection

import logging
import json


listen = ["default"]

r = redis.from_url(os.getenv("REDIS_URL", 'redis://localhost:6379'))

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d  - %(message)s')
    with Connection(r):
        logging.debug(listen)
        worker = Worker(listen)
        worker.work()


def respond(request_data):
    request_data = json.loads(request_data)
    try:
        user_response = parse.most_recent_msg(request_data)
        user_id = parse.get_user_id(request_data)
    except:
        logging.debug("PARSE FAILED={}".format(sys.exc_info()[0]))
        raise ParseException(sys.exc_info()[0])

    logging.debug("user_id={0}, user_response={1}".format(user_id, user_response))

    if tip.is_tip(user_response.lower()):
        logging.debug("TIP TEXT={}".format(user_response))
        tip_amount = tip.tip_amount(user_response)
        #s_api.post_message(user_id, "$[{}]({:.2f})".format("Confirm Tip", tip_amount), True)
        logging.debug("$[{}]({:.2f})".format("Confirm Tip", tip_amount))
        r.lpush("tip:" + user_id, tip_amount)
        return tip_amount

    if advent.user_exists(user_id):
        logging.debug("PROCESSING RESPONSE FOR={}".format(user_id))
        response = advent.respond(user_id, user_response).strip()
    else:
        logging.debug("CREATING NEW USER={}".format(user_id))
        response = advent.new_game(user_id).strip()

    r.rpush("conv:" + user_id, user_response)
    r.rpush("conv:" + user_id, response)

    logging.debug("user={0} game reply={1}".format(user_id,response))
    #s_api.post_message(user_id, response, True)
    return response

class ParseException(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)
