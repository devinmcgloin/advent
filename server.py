from flask import Flask, request
import json
from pysmooch.smooch import Smooch
import os
import adventure.loader as advent
import time
import logging
import sys
import pysmooch.smooch_parse as parse
import tip
import redis
from rq import Queue
from rq.job import Job
from worker import respond

s_api = Smooch(str(os.getenv("SMOOCH_KEY_ID")), str(os.getenv("SMOOCH_SECRET")))
r = redis.from_url(os.getenv("REDIS_URL", 'redis://localhost:6379'))
logging.debug(os.getenv("REDIS_URL", 'redis://localhost:6379'))
q = Queue("default", connection=r)

app = Flask(__name__)

@app.route('/hooks',methods=['POST'])
def process_mesage():
    """Listens at /hooks for posts to that url."""

    data = request.data.decode("utf-8")

    job = q.enqueue_call(func=respond,
                         args=(data,))

    logging.debug("JOB SENT")

    time.sleep(10)

    logging.debug(job)

    return job.result

@app.route('/')
def index():
    """Throws up HTML to index page to check if working properly"""
    return 'Welcome to Adventure'

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d  - %(message)s')
    #s_api.delete_all_webhooks()
    #webhook_id, webhook_secret = s_api.make_webhook("http://advent-term-120.herokuapp.com/hooks", "message:appUser")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
