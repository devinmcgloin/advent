import smooch

if __name__ == "__main__":
    smooch.delete_all_webhooks()
    smooch.create_webhook("http://advent-term-120.herokuapp.com/general", ["message:appUser"])
    smooch.create_webhook("http://advent-term-120.herokuapp.com/yesno", ["postback"])
