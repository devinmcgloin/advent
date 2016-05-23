import redis
import os
import smooch

r = redis.from_url(os.getenv("REDIS_URL", 'redis://localhost:6379'))

def is_highscore(score):
    """Determines if a score is a high score"""
    pass

def add_user_scoreboard(user_id, score):
    """Adds the specified user to the score board"""
    r.zadd("highscores", score, user_id)
    pass

def get_top_ten():
    """Gets the top ten scores, and returns a formatted list of the best players.
    Displays only firstname and last initial"""
    pass

def get_score(score_text):
    """Takes the standard output score text and returns the score"""
    pass
