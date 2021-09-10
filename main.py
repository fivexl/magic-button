import os
import uuid
import helpers_slack
import helpers_git
import helpers_time
from time import sleep, timezone

from slack_bolt.adapter.socket_mode import SocketModeHandler


if __name__ == "__main__":

    # Get job parameters
    build_job_name = os.environ['BUILD_JOB_NAME']
    build_job_url = os.environ['BUILD_JOB_URL']
    current_commit_id = os.environ['CURRENT_GIT_COMMIT']
    repo_name = os.environ['REPOSITORY_NAME']
    repo_url = os.environ['REPOSITORY_URL']
    slack_channel_name = os.environ['SLACK_CHANNEL_NAME']
    branches_to_promote = os.environ['BRANCHES_TO_PROMOTE'].split()
    timeout_minutes = int(os.environ['TIMEOUT_MINUTES'])
    timezone = os.environ['TIMEZONE']
    production_branch = os.environ['PRODUCTION_BRANCH']
    slack_bot_token = os.environ["SLACK_BOT_TOKEN"]

    ok_id = uuid.uuid4().hex
    nok_id = uuid.uuid4().hex
    app = helpers_slack.init_app(slack_bot_token, ok_id, nok_id)

    committer_email = helpers_git.get_committer_email_for_ref(current_commit_id)
    committer_slack_id = helpers_slack.user_id_by_email(app, committer_email)
    commiter_id = committer_slack_id if committer_slack_id is not None else committer_email
    author_email = helpers_git.get_author_email_for_ref(current_commit_id)
    author_slack_id = helpers_slack.user_id_by_email(app, author_email)
    author_id = author_slack_id if author_slack_id is not None else author_email
    commit_msg = helpers_git.get_commit_message_for_ref(current_commit_id)

    text_for_request = f'Job `{build_job_name}` requires approval to proceed.\n'
    text_for_request += 'If approved will promote commit(s) below to branch '
    text_for_request += ' and '.join(f'`{branch}`' for branch in branches_to_promote)
    text_for_request += f' in repository `{repo_name}`'
    text_for_request += f'\nJob will be autocanceled in {timeout_minutes} minutes if no action taken.\n\n'
    text_for_request += 'Details:\n'
    text_for_request += f'Job URL: {build_job_url}\n'
    text_for_request += f'Commit message: `{commit_msg}`; commit id `{current_commit_id}`\n\n'
    text_for_request += f'Committer: <@{commiter_id}>\n'
    text_for_request += f'Author: <@{author_id}>\n\n'

    for branch in branches_to_promote:
        text_for_request += helpers_git.generate_diff(branch, current_commit_id, repo_url)
    text_for_request += helpers_time.generate_time_based_message(production_branch, branches_to_promote, timezone)

    # Truncate too long messages to prevent Slack from posting them as several messages
    # We saw Slack splitting message into two after 3800 but haven't found any documentation
    # So number is more or less made up and needs further verification.
    if len(text_for_request) > 3500:
        text_for_request = text_for_request[:3500]
        text_for_request += '\ntoo long message - the rest was truncated. Use link above to see full diff'

    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"], trace_enabled=True).connect()

    blocks_json = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text_for_request
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Approve",
                            "emoji": True
                        },
                        "value": "click_me_123",
                        "style": "primary",
                        "action_id": ok_id,
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
                            "text": "Cancel",
                            "emoji": True
                        },
                        "value": "click_me_123",
                        "style": "danger",
                        "action_id": nok_id
                    }
                ]
            }
        ]

    message_deploy = app.client.chat_postMessage(
        channel=slack_channel_name,
        text="My Text",
        blocks=blocks_json
    )
    sleep(timeout_minutes*60) # Time in seconds

    # Why to keep auto canceled messages
    print('No response from user. Deliting message...')
    app.client.chat_delete(channel=message_deploy['channel'], ts=message_deploy['ts'])

    SocketModeHandler(app).close()
