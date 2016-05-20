"""The Adventure game.

Copyright 2010-2015 Brandon Rhodes.  Licensed as free software under the
Apache License, Version 2.0 as detailed in the accompanying README.txt.

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
#r = redis.Redis(host='localhost', port=6379)

def user_exists(user_id):
    return r.exists(user_id)

def new_game(user_id, seed=None):
    """Create new game"""
    logging.debug("creating new came for {}".format(user_id))
    game = Game(seed)
    load_advent_dat(game)
    game.start()
    response = format_response(game.output)
    r.set(user_id, game.t_suspend())
    return response

def respond(user_id, user_response):
    """Gets the game response for a specific user_id and user_response"""
    game = Game.resume(r.get(user_id))
    user_tupl_resp = tuple(user_response.lower().split(" "))
    response = format_response(game.do_command(user_tupl_resp))
    r.set(user_id, game.t_suspend())
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
    clean_response = response.replace("\n"," ").lower().strip().split(".")
    return ".\n".join(map((lambda s: s.strip().capitalize()),clean_response))
