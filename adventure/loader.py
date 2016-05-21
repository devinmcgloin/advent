"""
Handles interfacing with the Adventure module.
"""

#------------------------------------------
from .game import Game
from time import sleep
import os
import re


from .data import parse
import redis
import logging

r = redis.from_url(os.environ.get("REDIS_URL"))

capitalize = ["don", "woods", "i", "willie", "crowther.", "devin", "mcgloin"]

def user_exists(user_id):
    return r.exists("save:" + user_id)

def new_game(user_id, seed=None):
    """Create new game"""
    logging.debug("creating new came for {}".format(user_id))
    game = Game(seed)
    load_advent_dat(game)
    game.start()
    response = format_response(game.output)
    r.set("save:" + user_id, game.t_suspend())
    return response

def respond(user_id, user_response):
    """Gets the game response for a specific user_id and user_response"""
    game = Game.resume(r.get("save:" + user_id))
    user_tupl_resp = tuple(user_response.lower().split(" "))
    response = format_response(game.do_command(user_tupl_resp))
    r.set("save:" + user_id, game.t_suspend())
    return response

def reset_game(user_id, seed=None):
    """Clears the game for a specific user_id, need to wipe Memory and file game"""
    logging.debug("deleting save for {}".format(user_id))
    r.delete(user_id)

def load_advent_dat(data):
    """Called for each came object"""
    datapath = os.path.join(os.path.dirname(__file__), 'advent.dat')
    with open(datapath, 'r') as datafile:
        parse(data, datafile)

def format_response(response):
    clean_response = response.replace("\n"," ").lower().strip()
    clean_response = " ".join([cap(s) for s in clean_response.split(" ")])
    rsp = "\n".join(accum_words(clean_response))
    return rsp

def cap(s):
    if s == "mcgloin":
        return "McGloin"
    if s in capitalize:
        return s.capitalize()
    return s

def first_upper(s):
    """Capitalizes the first letter, leaves everything else alone"""
    return re.sub('([a-zA-Z])', lambda x: x.groups()[0].upper(), s, 1)

def accum_words(response):
    """Takes words split by space and capitalizes first character and special cases"""
    cleaned_sentences = []
    regex = re.compile("(\!+|\?+|\.+)")
    split = re.split(regex, response)
    print(split)
    puncts = split[1::2]
    sentences = split[::2]
    for s, p in zip(sentences, puncts):
        sent = s.strip()
        pun = p.strip()
        cleaned_sentences.append(sent.capitalize() + pun)
    return cleaned_sentences
