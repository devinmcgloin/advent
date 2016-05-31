import logging
import re

import smooch

from adventure import advent
from conn import r, q
from conv_mechanics.scheduler import respond


def start_new(postback_payload, user_id):
    if postback_payload.endswith("yes"):
        advent.new_game(user_id)
        response = advent.respond(user_id, "no")
        smooch.send_message(user_id, response, True)
        r.delete("yesno:" + user_id)
        return True
    elif postback_payload.endswith("no"):
        r.delete("yesno:" + user_id)
        r.delete("save:" + user_id)
        smooch.send_message(user_id, "Ok.", True)
        return True
    else:
        logging.error("Invalid postback={}".format(postback_payload))
        return False


def restart(postback_payload, user_id):
    if postback_payload.endswith("yes"):
        advent.new_game(user_id)
        response = advent.respond(user_id, "no")
        smooch.send_message(user_id, response, True)
        r.delete("yesno:" + user_id)
        return True
    elif postback_payload.endswith("no"):
        r.delete("yesno:" + user_id)
        smooch.send_message(user_id, "Ok.", True)
        return True
    else:
        logging.error("Invalid postback={}".format(postback_payload))
        return False


def game_fallback(postback_payload, user_id):
    if postback_payload.endswith("yes"):
        response = advent.respond(user_id, "yes")

        # Checking if user has asked to end the game.
        if re.search("You scored \d+ out of a possible \d+ using \d+ turns.", response):
            respond(user_id, response)
            advent.new_game(user_id)
            r.set("yesno:" + user_id, "new_game")
            smooch.send_postbacks(user_id, "Do you want to play again?",
                                  [("Yes", "start_new_yes"),
                                   ("No", "start_new_no")])
            return True
        q.enqueue_call(func=respond, args=(user_id, response))
        r.delete("yesno:" + user_id)
        return True
    elif postback_payload.endswith("no"):
        response = advent.respond(user_id, "no")
        q.enqueue_call(func=respond, args=(user_id, response))
        r.delete("yesno:" + user_id)
        return True
    else:
        logging.error("Invalid postback={}".format(postback_payload))
        return False


def process_postback(postback_payload, user_id):
    if not r.get("yesno:" + user_id):
        return True
    elif postback_payload.startswith("restart"):
        return restart(postback_payload, user_id)
    elif postback_payload.startswith("start_new"):
        return start_new(postback_payload, user_id)
    elif re.match("(yes|no)", postback_payload):
        return game_fallback(postback_payload, user_id)
    else:
        logging.error("Invalid postback={}".format(postback_payload))
        return False
