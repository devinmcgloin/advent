import smooch


def respond(user_id, response):
    smooch.send_message(user_id, response)
    # for msg in response.split("\n"):
    #     smooch.send_message(user_id, msg)
