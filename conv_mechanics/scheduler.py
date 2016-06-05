import random
import smooch


def respond(user_id, response):

    messages = response.split("\n")

    stop = random.randint(2, 4)
    start = 0

    while messages[start:stop]:
        msg = "\n".join(messages[start:stop])

        if msg == "":
            continue

        smooch.send_message(user_id, msg)
        start = stop
        stop += random.randint(2, 4)
