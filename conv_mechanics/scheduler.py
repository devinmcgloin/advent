import random
import smooch


def respond(user_id, response):

    messages = response.split("\n")

    spacing = random.randint(2, 4)
    start = 0
    stop = spacing

    while messages[start:stop]:
        smooch.send_message(user_id, "\n".join(messages[start:stop]))
        start = stop
        stop += spacing
