from langchain.tools import tool

from app.slack.bot import (
    slack_client,
)


@tool
def send_message(
    channel_id: str,
    text: str,
):
    """
    Send Slack message.
    """

    slack_client.chat_postMessage(
        channel=channel_id,
        text=text,
    )

    return "Message sent"


@tool
def upload_file(
    channel_id: str,
    file_path: str,
):
    """
    Upload file to Slack.
    """

    slack_client.files_upload_v2(
        channel=channel_id,
        file=file_path,
    )

    return "File uploaded"