from fastapi import APIRouter
from fastapi import Request

from app.slack.handlers import (
    process_user_message,
    process_transcript_file,
)


router = APIRouter()


@router.post("/events")
async def slack_events(
    request: Request,
):

    payload = await request.json()

    # --------------------------
    # Slack URL Verification
    # --------------------------

    if payload.get("type") == "url_verification":

        return {
            "challenge":
            payload["challenge"]
        }

    event = payload.get(
        "event",
        {}
    )

    # Ignore bot messages

    if event.get("bot_id"):
        return {
            "status": "ignored"
        }

    event_type = event.get(
        "type"
    )

    # --------------------------
    # Message Event
    # --------------------------

    if event_type == "message":

        slack_user_id = event.get(
            "user"
        )

        channel_id = event.get(
            "channel"
        )

        text = event.get(
            "text",
            ""
        )

        files = event.get(
            "files",
            []
        )

        # ----------------------
        # Transcript Upload
        # ----------------------

        if files:

            file_url = files[0].get(
                "url_private"
            )

            process_transcript_file(
                slack_user_id=
                slack_user_id,
                channel_id=
                channel_id,
                file_url=file_url,
            )

            return {
                "status":
                "transcript_processed"
            }

        # ----------------------
        # Text Message
        # ----------------------

        process_user_message(
            slack_user_id=
            slack_user_id,
            channel_id=
            channel_id,
            text=text,
        )

    return {
        "status": "ok"
    }