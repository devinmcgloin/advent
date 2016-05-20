def get_user_id(conversation):
    return conversation["appUser"]["_id"]

def most_recent_msg(converstation, msg_from="appUser"):
    msessages = [ x for x in conversation["messages"] if x["role"] == "appUser"]
    return messages[0]
