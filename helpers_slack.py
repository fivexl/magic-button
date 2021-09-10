import os

from slack_bolt import App
from slack_sdk.errors import SlackApiError

def init_app(slack_bot_token, approve_action_id, cancel_action_id):
    app = App(token=slack_bot_token)

    @app.action(approve_action_id)
    def approve_request(ack, respond, body):
    # Acknowledge action request
        ack()
        print(body)
        username = body['user']['username']
        original_text = body['message']['blocks'][0]['text']['text']
        respond(original_text + f'\n\nApproved by {username} 👍')
        os._exit(0)

    @app.action(cancel_action_id)
    def approve_request(ack, respond, body):
        # Acknowledge action request
        ack()
        print(body)
        username = body['user']['username']
        original_text = body['message']['blocks'][0]['text']['text']
        respond(original_text + f'\n\nCanceled by {username} ❌')
        os._exit(1)

    @app.middleware
    def middleware_func(logger, body, next):
        logger.info(f"request body: {body}")
        next()

    return app

def user_id_by_email(app, email):
    try:
        result = app.client.users_lookupByEmail(email=email)
        return result['user']['id']
    except SlackApiError as err:
        if err.response['error'] == 'users_not_found':
            return None

    return None