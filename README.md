[![FivexL](https://releases.fivexl.io/fivexlbannergit.jpg)](https://fivexl.io/)

# Magin Button

Deployment confiramtion button for Slack

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
