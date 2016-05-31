"""
Simple terminal interface to a redis instance in order to test game mechanics.

You can provide optional command line arguments to connect to a redis instance of your choice.
"""

import sys

import redis

from adventure import advent

if __name__ == '__main__':
    if len(sys.argv) > 1:
        print("Setting custom redis url={}".format(sys.argv[1]))
        advent.r = redis.from_url(sys.argv[1])
    user_id = input("Enter your user_id: ")
    if advent.user_exists(user_id):
        game_output = advent.respond(user_id, "look")
    else:
        game_output = advent.new_game(user_id)
    while True:
        print("\n\n" + game_output)
        user_in = input("> ").strip()
        game_output = advent.respond(user_id, user_in)
