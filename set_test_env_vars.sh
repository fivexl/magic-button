export BUILD_JOB_NAME=local-test
export BUILD_JOB_URL=http://whatever.com
export CURRENT_GIT_COMMIT=$(git rev-parse HEAD)
export REPOSITORY_NAME=$(basename $(git rev-parse --show-toplevel))
export REPOSITORY_URL=https://github.com/fivexl/magic-button
export BRANCHES_TO_PROMOTE=test
export TIMEOUT_MINUTES=1
export TIMEZONE=$(cat /etc/timezone)
export PRODUCTION_BRANCHES=release
export SLACK_CHANNEL_NAME=magic-button
# Set SLACK_APP_TOKEN and SLACK_BOT_TOKEN manualy
[ -z "${SLACK_APP_TOKEN}" ] && echo "Make sure to set SLACK_APP_TOKEN"
[ -z "${SLACK_BOT_TOKEN}" ] && echo "Make sure to set SLACK_BOT_TOKEN"