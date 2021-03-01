# Slack Support Channel Scraper
This tool acts as a companion to a weekly meeting that you can have in your team to analyze support requests that you receive on your support channel.

To make use of this tool, you should do the following:
1. Organize a weekly meeting to look at support requests.
2. Go to Slack, and create a bunch of emojis that share a specific prefix. For example: `sup_feature-request`, `sup_manual-action`, `sup_bug`, etc.
3. In addition, make sure to create an emoji called `sup_ignore`.
4. Copy this script to your local machine, and install its requirements.
5. Store a Slack token into some environment variable.
6. Provide a file called `scraper_config.yaml`, which should look as follows:
```yaml
slack_channel_id: CBP3GTFTQ # the ID of the slack channel
start_date: 2021-02-04  # the date from which you want to start analyzing requests
slack_token_env_variable: SVC_SLACK_TOKEN # the environment variable where you stored the token
reaction_prefix: sup  # the prefix of the reactions
```
7. Hold your weekly meeting, go over the support requests, discuss them, and add the appropriate reactions to them
8. Run this tool, and look at the graphs. The current graphs will show you the number of support requests per week, as well as the distribution of the requests among the different reactions
9. Make decisions, iterate, and improve!