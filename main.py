import os
import uuid
import helpers_slack
import helpers_git
import helpers_time
from time import sleep, timezone

from slack_bolt.adapter.socket_mode import SocketModeHandler

DETAILS_BLOCK_ID = 'details'
TIMEOUT_RETURN_CODE = 200
USER_CANCEL_RETURN_CODE = 100

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
    commiter_id = f'<@{committer_slack_id}>' if committer_slack_id is not None else committer_email
    author_email = helpers_git.get_author_email_for_ref(current_commit_id)
    author_slack_id = helpers_slack.user_id_by_email(app, author_email)
    author_id = f'<@{author_slack_id}>' if author_slack_id is not None else author_email
    commit_msg = helpers_git.get_commit_message_for_ref(current_commit_id)

    text_for_request = 'If approved will promote commit(s) below to branch '
    text_for_request += ' and '.join(f'`{branch}`' for branch in branches_to_promote)
    text_for_request += f' in repository `{repo_name}`'
    details = f'Job URL: {build_job_url}\n'
    details += f'Commit message: `{commit_msg}`\n'
    details += f'Commit id: `{current_commit_id}`\n'
    details += f'Committer: {commiter_id}\n'
    details += f'Author: {author_id}\n\n'

    for branch in branches_to_promote:
        details += helpers_git.generate_diff(branch, current_commit_id, repo_url)
    details += helpers_time.generate_time_based_message(production_branch, branches_to_promote, timezone)

    # Truncate too long messages to prevent Slack from posting them as several messages
    # We saw Slack splitting message into two after 3800 but haven't found any documentation
    # So number is more or less made up and needs further verification.
    if len(text_for_request) > 3500:
        details = details[:3500]
        details += '\ntoo long message - the rest was truncated. Use link above to see full diff'

    header_for_header = f'Approval request for job {build_job_name}'

    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"], trace_enabled=True).connect()

    blocks_json = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": header_for_header
                },
                "block_id": "header"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text_for_request
                },
                "block_id": "request_info"
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": details
                },
                "block_id": DETAILS_BLOCK_ID
            },
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f'This message will self-destruct 🕶️🧨💥 and job will be auto-cancel in {timeout_minutes} minutes if no action is taken'
                    }
                ],
                "block_id": "context_self_destruct"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f'☝️ If you configure your commit email to match your Slack profile email then next time I will be able to tag you!'
                    }
                ],
                "block_id": "tag_suggestion"
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
                                "text": f"Do you really want to approve deploy of {build_job_name}???"
                            },
                            "confirm": {
                                "type": "plain_text",
                                "text": "Super duper sure"
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

    print('Sending message out...')
    message_deploy = app.client.chat_postMessage(
        channel=slack_channel_name,
        text=f'Approval request for {build_job_url}',
        blocks=blocks_json
    )

    print('Waiting for user to respond...')
    sleep(timeout_minutes*60) # Time in seconds

    # Why to keep auto canceled messages
    print('No response from user. Deliting message...')
    app.client.chat_delete(channel=message_deploy['channel'], ts=message_deploy['ts'])
    app.client.chat_postMessage(channel=message_deploy['channel'],
        blocks=[
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f'Approval request for job {build_job_url} canceld by timeout after {timeout_minutes} min. Restart the build to get a new one'
                    }
                ],
            }
        ])

    SocketModeHandler(app).close()
    print(f'No reply from user. Auto-cancel and return shell exit code {TIMEOUT_RETURN_CODE}')
    os._exit(TIMEOUT_RETURN_CODE)
