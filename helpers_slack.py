import os

from slack_bolt import App
from slack_sdk.errors import SlackApiError

from main import DETAILS_BLOCK_ID
from main import USER_CANCEL_RETURN_CODE

def init_app(slack_bot_token, approve_action_id, cancel_action_id):
    app = App(token=slack_bot_token)

    @app.action(approve_action_id)
    def approve_request(ack, respond, body):
    # Acknowledge action request
        ack()
        print(body)
        print('User pressed approve. update message and exit 0')
        username = body['user']['username']
        original_text = ''
        for block in  body['message']['blocks']:
            if 'block_id' in block and block['block_id'] == DETAILS_BLOCK_ID:
                original_text = block['text']['text']
        respond(original_text + f'\n\nApproved by {username} 👍')
        print(f'Approved by user {username}. Exit with shell return code 0')
        os._exit(0)

    @app.action(cancel_action_id)
    def approve_request(ack, client, body):
        # Acknowledge action request
        ack()
        print(body)
        header_text = ''
        for block in  body['message']['blocks']:
            if 'type' in block and block['type'] == 'header':
                header_text = block['text']['text']
        print('User pressed cancel. Delete message and exit 1')
        client.chat_delete(channel=body['container']['channel_id'], ts=body['container']['message_ts'])
        app.client.chat_postEphemeral(channel=body['container']['channel_id'], user=body['user']['id'], text=f'{header_text} canceled by you and deleted to keep approval log nice and clean')
        print(f'Canceled by user. Exit with shell return code {USER_CANCEL_RETURN_CODE}')
        os._exit(USER_CANCEL_RETURN_CODE)

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