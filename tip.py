"""
utility functions to determine if a command is a tip or not.
"""

import re

is_tip_regex = re.compile("^tip *\$?(?:0|[1-9]\d{0,2}(?:,?\d{3})*)(?:\.\d+)?$")
amount_regex = re.compile("-?(?:0|[1-9]\d{0,2}(?:,?\d{3})*)(?:\.\d+)?$")


def is_tip(user_response):
    if re.match(is_tip_regex, user_response) is not None:
        return True
    return False


def tip_amount(user_response):
    matches = re.findall(amount_regex, user_response)
    return max(map(float, matches))
