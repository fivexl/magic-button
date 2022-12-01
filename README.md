[![FivexL](https://releases.fivexl.io/fivexlbannergit.jpg)](https://fivexl.io/)

# Magin Button

Deployment confirmation button for Slack

# Configuration

Configuration is done via env variables

* `SLACK_BOT_TOKEN` - Slack bot token. Mandatory parameter. scopes: channels:history, chat:write, reactions:read, users:read.email, users:read
* `SLACK_APP_TOKEN` - Slack app token. Mandatory parameter. scopes: connections:write

# Slack App manifect example 
```yaml
_metadata:
  major_version: 1
  minor_version: 1
display_information:
  name: MagicButton
  description: Deployment confirmation
  background_color: "#2645a3"
features:
  bot_user:
    display_name: MagicButton
    always_online: false
oauth_config:
  scopes:
    bot:
      - channels:history
      - chat:write
      - reactions:read
      - users:read.email
      - users:read
settings:
  interactivity:
    is_enabled: true
  org_deploy_enabled: false
  socket_mode_enabled: true
  token_rotation_enabled: false
```

# report.json example
```json
{
  "timestamp": 1669891821,
  "approval_code": 0,
  "usernames": [
    "vladimir.samoylov"
  ],
  "teams": [
    "fivexl"
  ],
  "channel": "magic-button",
  "message": "Approval request for job local-test"
}
```

# GitHub Workflow Example
```
      # Repo metadata - output of this step will be used by the later steps. Search for steps.repo.outputs to see where
      - name: Repo metadata
        id: repo
        uses: actions/github-script@v3
        with:
          script: |
            const repo = await github.repos.get(context.repo)
            return repo.data

      - name: Approval
        id: approval
        if: steps.checkout.outcome == 'success'
        env:
          MAGIC_BUTTON_VERSION: "v0.2.0"
          SLACK_BOT_TOKEN: "${{ secrets.SLACK_BOT_TOKEN }}"
          SLACK_APP_TOKEN: "${{ secrets.SLACK_APP_TOKEN }}"
          SLACK_CHANNEL_NAME: "${{ secrets.SLACK_CHANNEL_NAME }}"
          BUILD_JOB_NAME: "${{ github.event.repository.name }}"
          BUILD_JOB_URL: "${{ fromJson(steps.repo.outputs.result).html_url }}/actions"
          PRODUCTION_BRANCHES: release
          BRANCHES_TO_PROMOTE: "${{ env.GIT_DESTINATION_BRANCH }}"
          TIMEOUT_MINUTES: 1
          REPOSITORY_URL: "${{ fromJson(steps.repo.outputs.result).html_url }}"
        run: >
          mkdir -p magic-button/reports && chmod 777 magic-button/reports
          && docker run --rm
          -v "$(pwd)/.git":/app/.git
          -v "$(pwd)/magic-button/reports":/app/reports
          -e SLACK_BOT_TOKEN -e SLACK_APP_TOKEN -e BUILD_JOB_NAME -e BUILD_JOB_URL
          -e CURRENT_GIT_COMMIT="$(git rev-parse HEAD)" -e REPOSITORY_NAME="$(basename $(git rev-parse --show-toplevel))"
          -e REPOSITORY_URL -e BRANCHES_TO_PROMOTE -e TIMEOUT_MINUTES -e TIMEZONE="Europe/Oslo" 
          -e PRODUCTION_BRANCHES -e SLACK_CHANNEL_NAME
          ghcr.io/fivexl/magic-button:${{ env.MAGIC_BUTTON_VERSION }}
          && ls -all magic-button/reports && cat magic-button/reports/report.json
        continue-on-error: true
```