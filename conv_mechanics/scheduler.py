import random
import smooch


def respond(user_id, response):

    messages = response.split("\n")

    stop = random.randint(2, 4)
    start = 0

    while messages[start:stop]:
        smooch.send_message(user_id, "\n".join(messages[start:stop]))
        start = stop
        stop += random.randint(2, 4)
