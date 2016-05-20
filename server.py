from flask import Flask, request
import json
from smooch import Smooch
import os
import adventure.loader as advent
import time

s_api = Smooch(str(os.getenv("SMOOCH_KEY_ID")), str(os.getenv("SMOOCH_SECRET")))

app = Flask(__name__)

@app.route('/hooks',methods=['POST'])
def process_mesage():
    """Listens at /hooks for posts to that url."""
    data = json.loads(request.data)
    print("INCOMING MESSAGE")
    time.sleep(10)
    print(data)
    # we get back an array of messages
    user_response = data["messages"][0]["text"]
    user_id = data["appUser"]["_id"]
    print("user={0}, said={1}".format(user_id, user_response))

    if advent.user_exists(user_id):
        response = advent.respond(user_id, user_response)
    else:
        response = advent.new_game(user_id)

    print("game reply={0}".format(response))

    s_api.post_message(user_id, response, True)
    advent.db_save()
    return "OK"

@app.route('/')
def index():
    """Throws up HTML to index page to check if working properly"""
    return 'Welcome to Adventure'

if __name__ == '__main__':
    s_api.delete_all_webhooks()
    webhook_id, webhook_secret = s_api.make_webhook("http://advent-term-120.herokuapp.com/hooks", "message:appUser")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
