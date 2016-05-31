"""
General smooch parsing utilities
"""


def get_user_id(conversation):
    """returns the _id used to send smooch requests"""
    return conversation["appUser"]["_id"]


def most_recent_msg(conversation, msg_from="appUser"):
    """returns most recent message from a given user type"""
    messages = [x for x in conversation["messages"] if x["role"] == msg_from]
    return messages[0]["text"]


def get_postback_payload(postback):
    return postback["postbacks"][0]["action"]["payload"]


    # [{
    #     "_id": "571530ee4fae94c32b78b170",
    #     "type": "postback",
    #     "text": "Read more",
    #     "payload": "1234"
    # }]
