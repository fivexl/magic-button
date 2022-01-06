import os
import uuid
import helpers_slack
import helpers_git
import helpers_time
from time import sleep

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
    production_branches = os.environ['PRODUCTION_BRANCHES'].split()
    slack_bot_token = os.environ["SLACK_BOT_TOKEN"]

    print(f'branches_to_promote: {branches_to_promote}')
    print(f'production_branches: {production_branches}')

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
    details += helpers_time.generate_time_based_message(production_branches, branches_to_promote, timezone)

    # Generate separate diff blocks for every branch
    diffs = []
    for idx, branch in enumerate(branches_to_promote):
        diff = helpers_git.generate_diff(branch, current_commit_id, repo_url)
        diff_id = f'diff_{idx}'
        diffs.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": diff,
                },
                "block_id": diff_id
            }
        )

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
            }
    ]
    blocks_json += diffs
    self_destruct_msg = ('This message will self-destruct 🕶️🧨💥 and job will be '
                         + f'auto-cancel in {timeout_minutes} minutes if no action is taken')
    email_msg = ('☝️ If you configure your commit email to match your Slack profile '
                 + 'email then next time I will be able to tag you!')
    blocks_json += [
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": self_destruct_msg
                    }
                ],
                "block_id": "context_self_destruct"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": email_msg
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
                        "action_id": nok_id,
                        "confirm": {
                            "title": {
                                "type": "plain_text",
                                "text": "Are you sure?"
                            },
                            "text": {
                                "type": "mrkdwn",
                                "text": f"Do you really want to cancel {build_job_name}???"
                            },
                            "confirm": {
                                "type": "plain_text",
                                "text": "Yes! That is the one I want!"
                            },
                            "deny": {
                                "type": "plain_text",
                                "text": "No! I pressed a wrong button!"
                            }
                        }
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
    sleep(timeout_minutes*60)  # Time in seconds

    # Why to keep auto canceled messages
    print('No response from user. Deliting message...')
    app.client.chat_delete(channel=message_deploy['channel'], ts=message_deploy['ts'])
    post_cancel_msg = (f'Approval request for job {build_job_url} canceled '
                       + 'by timeout after {timeout_minutes} min.'
                       + ' Restart the build to get a new one')
    app.client.chat_postMessage(
        channel=message_deploy['channel'],
        blocks=[
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": post_cancel_msg
                    }
                ],
            }
        ]
    )

    SocketModeHandler(app).close()
    print(f'No reply from user. Auto-cancel and return shell exit code {TIMEOUT_RETURN_CODE}')
    os._exit(TIMEOUT_RETURN_CODE)
