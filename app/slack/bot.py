from slack_sdk import WebClient

from app.config.settings import (
    settings,
)


slack_client = WebClient(
    token=settings.SLACK_BOT_TOKEN
)