import os
import logging
from time import sleep

from slack_bolt import App, logger
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.web import client

# Install the Slack app and get xoxb- token in advance
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# ID of channel you want to post message to
channel_name = "magic-button-test" #TODO: os.environ["SLACK_CHANNEL_NAME"]

# GitHub Project Name
github_project_name = "test-api" #TODO: os.environ["GIT_REPO_NAME"]

@app.action(github_project_name + "_yes")
def approve_request(ack, say):
    # Acknowledge action request
    ack()
    say("Great! I will do! Request approved 👍 !")
    #TODO: Replase existing message and remove buttons for prevert second click
    os._exit(0)

@app.action(github_project_name + "_no")
def approve_request(ack, say):
    # Acknowledge action request
    ack()
    say("Up to you! Request NOT approved :thumbsdown: !")
    #TODO: Replase existing message and remove buttons for prevert second click
    os._exit(1)


@app.middleware
def middleware_func(logger, body, next):
    logger.info(f"request body: {body}")
    next()

if __name__ == "__main__":
    # message = app.client.chat_postMessage(
    #     channel=channel_id,
    #     text="Test Message"
    # )
    # print(message)
    # logging.info(f'Message resp: {message}')
    # SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"], trace_enabled=True).connect()

    blocks_json = [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": f'Do you want to deploy project {github_project_name}? I will wait 30s',
                    "emoji": True
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Yes",
                            "emoji": True
                        },
                        "value": "click_me_123",
                        "style": "primary",
                        "action_id": github_project_name + "_yes",
                        "confirm": {
                            "title": {
                                "type": "plain_text",
                                "text": "Are you sure?"
                            },
                            "text": {
                                "type": "mrkdwn",
                                "text": "Do you really want to deploy it???"
                            },
                            "confirm": {
                                "type": "plain_text",
                                "text": "Do it"
                            },
                            "deny": {
                                "type": "plain_text",
                                "text": "Stop, I've changed my mind!"
                            }
                        }
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "No",
                            "emoji": True
                        },
                        "value": "click_me_123",
                        "style": "danger",
                        "action_id": github_project_name + "_no"
                    }
                ]
            }
        ]

    message_deploy = app.client.chat_postMessage(
        channel=channel_name,
        text="My Text",
        blocks=blocks_json
    )
    sleep(30) # Time in seconds
    SocketModeHandler(app).close()
