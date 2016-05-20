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

r = redis.from_url(os.environ.get("REDIS_URL"))
#r = redis.Redis(host='localhost', port=6379)

def user_exists(user_id):
    return r.exists(user_id)

def new_game(user_id, seed=None):
    """Create new game"""
    print("CREATING NEW GAME")
    game = Game(seed)
    load_advent_dat(game)
    game.start()
    response = game.output
    print(response)
    r.set(user_id, game.t_suspend())
    print("RESPONDING")
    return response

def respond(user_id, user_response):
    """Gets the game response for a specific user_id and user_response"""
    game = Game.resume(r.get(user_id))
    user_tupl_resp = tuple(user_response.split(" "))
    response = game.do_command(user_tupl_resp)
    r.set(user_id, json.dumps(game))
    return response

def reset_game(user_id, seed=None):
    """Clears the game for a specific user_id, need to wipe memory and file game"""
    r.delete(user_id)

def load_advent_dat(data):
    """Called for each came object"""
    datapath = os.path.join(os.path.dirname(__file__), 'advent.dat')
    with open(datapath, 'r') as datafile:
        parse(data, datafile)