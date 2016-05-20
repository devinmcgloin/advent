"""
See https://github.com/whatsahoy/smooch-python
"""

import logging
import jwt
import json
import os
import requests

class Smooch:
    class APIError(Exception):
        def __init__(self, response):
            self.response = response

        def __str__(self):
            return str(self.response)

    def __init__(self, key_id, secret):
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d  - %(message)s')
        logging.debug("KEY_ID={}".format(key_id))
        logging.debug("SECRET={}".format(secret))
        self.key_id = key_id
        self.secret = secret
        self.jwt_token = jwt.encode({'scope': 'app'},
                                    secret,
                                    algorithm='HS256',
                                    headers={"kid": key_id, "alg": "HS256"}).decode("utf-8")

        logging.debug(self.jwt_token)

    def jwt_for_user(key_id, secret, user_id):
        return jwt.encode({'scope': 'appUser', 'userId': user_id},
                          secret,
                          algorithm='HS256',
                          headers={"kid": key_id, "alg": "HS256"})

    def user_jwt(self, user_id):
        return self.jwt_for_user(self.key_id, self.secret, user_id)


    def ask(self, endpoint, data, method='get', files=None):
        url = "https://api.smooch.io/v1/{0}".format(endpoint)

        if method == 'get':
            caller_func = requests.get
        elif method == 'post':
            caller_func = requests.post
        elif method == 'put':
            caller_func = requests.put
        elif method == 'delete':
            caller_func = requests.delete

        headers = self.headers
        if files:
            headers.pop('content-type')

        logging.debug("headers={}".format(headers))

        response = caller_func(url=url, headers=headers, json=data)
        logging.debug(response.content)

        if response.status_code == 200 or response.status_code == 201:
            return response
        else:
            raise Smooch.APIError(response)


    def post_message(self, user_id, message, sent_by_maker=False):
        role = "appUser"
        if sent_by_maker:
            role = "appMaker"

        data = {"text": message, "role": role}
        return self.ask('appusers/{0}/conversation/messages'.format(user_id),
                        data,
                        'post')



    def get_user(self, user_id):
        return self.ask('appusers/{0}'.format(user_id), {}, 'get')

    def update_user(self, user_id, data):
        return self.ask('appusers/{0}'.format(user_id), data, 'put')

    def init_user(self, user_id, device_id):
        data = {
            "device": {
                "id": device_id,
                "platform": "other"
            },
            "userId": user_id
        }
        return self.ask('init', data, 'post')

    def precreate_user(self, user_id):
        data = {
            "userId": user_id
        }
        return self.ask('appusers', data, 'post')

    def get_webhooks(self):
        return self.ask('webhooks', {}, 'get')

    def make_webhook(self, target, triggers=None):
        if triggers:
            return self.ask('webhooks', {"target": target, "triggers": triggers}, 'post')
        else:
            return self.ask('webhooks', {"target": target}, 'post')


    def update_webhook(self, webhook_id, target, triggers):
        return self.ask('webhooks/{0}'.format(webhook_id), {"target": target, "triggers": triggers}, 'put')

    def delete_webhook(self, webhook_id):
        return self.ask('webhooks/{0}'.format(webhook_id), {}, 'delete')

    def delete_all_webhooks(self):
        webhooks_response = self.get_webhooks()
        webhooks = webhooks_response.json()['webhooks']

        responses = []
        for webhook in webhooks:
            dr = self.delete_webhook(webhook['_id'])
            responses.append(dr)

        return responses


    def ensure_webhook_exist(self, trigger, webhook_url):
        log.debug("Ensuring that webhook exist: %s; %s", trigger, webhook_url)
        r = self.get_webhooks()
        data = r.json()

        message_webhook_id = False
        message_webhook_needs_updating = False
        webhook_secret = None

        for value in data["webhooks"]:
            if trigger in value["triggers"]:
                message_webhook_id = value["_id"]
                webhook_secret = value["secret"]
                if value["target"] != webhook_url:
                    message_webhook_needs_updating = True
                break

        log.debug("message_webhook_id: %s", message_webhook_id)
        log.debug("message_webhook_needs_updating: %s", message_webhook_needs_updating)
        if not message_webhook_id:
            log.debug("Creating webhook")
            r = self.make_webhook(webhook_url, [trigger])
            data = r.json()
            message_webhook_id = data["webhook"]["_id"]
            webhook_secret = data["webhook"]["secret"]

        if message_webhook_needs_updating:
            log.debug("Updating webhook")
            self.update_webhook(message_webhook_id, webhook_url, [trigger])

        return message_webhook_id, webhook_secret

    @property
    def headers(self):
        return {
            'authorization': 'Bearer {0}'.format(self.jwt_token),
            'content-type': 'application/json'
        }
