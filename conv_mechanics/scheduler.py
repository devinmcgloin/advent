import smooch


def respond(user_id, response):
    if response == "" or user_id == "":
        return

    smooch.send_message(user_id, response)
