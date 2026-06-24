import requests
import logging
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.database.connection import SessionLocal

from app.database.repository import (
    get_or_create_session,
    save_client_profile,
)

from app.workflows.router import classify_request

# ✅ SERVICES LAYER
from app.services.proposal_service import generate_proposal
from app.services.revision_service import revise_proposal
from app.services.qa_service import answer_question

# Tools
from app.tools.slack_tool import send_message, upload_file

logger = logging.getLogger(__name__)


# ----------------------------
# DB SESSION
# ----------------------------
def get_db():
    return SessionLocal()


# ----------------------------
# DOWNLOAD SLACK FILE
# ----------------------------
def download_slack_file(file_url: str):
    logger.info(f"Downloading file from Slack: {file_url}")
    response = requests.get(
        file_url,
        headers={
            "Authorization": f"Bearer {settings.SLACK_BOT_TOKEN}"
        },
    )
    response.raise_for_status()
    logger.info("Successfully downloaded Slack file")
    return response.text


# ----------------------------
# TRANSCRIPT HANDLER
# ----------------------------
def process_transcript_file(
    slack_user_id: str,
    channel_id: str,
    file_url: str,
):
    logger.info(f"Processing transcript upload for user {slack_user_id}")
    transcript = download_slack_file(file_url)

    process_user_message(
        slack_user_id=slack_user_id,
        channel_id=channel_id,
        text=transcript,
    )


# ----------------------------
# MAIN ENTRYPOINT
# ----------------------------
def process_user_message(
    slack_user_id: str,
    channel_id: str,
    text: str,
):
    logger.info(f"Received message from user {slack_user_id} in channel {channel_id}")
    db: Session = get_db()

    try:
        # Resolve a channel-specific session to support multiple threads/channels per user
        session_slack_user_id = f"{slack_user_id}:{channel_id}"
        session = get_or_create_session(
            db=db,
            slack_user_id=session_slack_user_id,
        )
        logger.info(f"Resolved database session ID: {session.id} for session user ID: {session_slack_user_id}")

        request_type = classify_request(text)
        logger.info(f"Classified request type as: '{request_type}'")

        # ======================================
        # QA FLOW
        # ======================================
        if request_type == "question":
            logger.info("Executing QA workflow")
            result = answer_question(
                db=db,
                session_id=session.id,
                slack_user_id=slack_user_id,
                channel_id=channel_id,
                user_question=text,
            )

            send_message.invoke(
                {
                    "channel_id": channel_id,
                    "text": result["answer"],
                }
            )
            return

        # ======================================
        # REVISION FLOW
        # ======================================
        if request_type == "revision":
            logger.info("Executing Revision workflow")
            result = revise_proposal(
                db=db,
                session_id=session.id,
                slack_user_id=slack_user_id,
                channel_id=channel_id,
                revision_request=text,
            )

            docx_path = result.get("docx_path")
            if docx_path:
                logger.info(f"Uploading revised DOCX: {docx_path}")
                upload_file.invoke(
                    {
                        "channel_id": channel_id,
                        "file_path": docx_path,
                    }
                )

            send_message.invoke(
                {
                    "channel_id": channel_id,
                    "text": "Proposal updated successfully.",
                }
            )
            return

        # ======================================
        # NEW PROPOSAL FLOW
        # ======================================
        logger.info("Executing Proposal Generation workflow")
        result = generate_proposal(
            db=db,
            session_id=session.id,
            slack_user_id=slack_user_id,
            channel_id=channel_id,
            transcript=text,
        )

        profile = result.get("client_profile", {})
        docx_path = result.get("docx_path")

        if docx_path:
            logger.info(f"Uploading generated proposal DOCX: {docx_path}")
            upload_file.invoke(
                {
                    "channel_id": channel_id,
                    "file_path": docx_path,
                }
            )

        missing_fields = profile.get("missing_fields", [])
        if missing_fields:
            send_message.invoke(
                {
                    "channel_id": channel_id,
                    "text":
                        "Proposal generated.\n\nMissing fields:\n"
                        + "\n".join(f"- {f}" for f in missing_fields),
                }
            )
        else:
            send_message.invoke(
                {
                    "channel_id": channel_id,
                    "text": "Proposal generated successfully.",
                }
            )

    except Exception as e:
        logger.error(f"Error occurred while processing message: {str(e)}", exc_info=True)
        send_message.invoke(
            {
                "channel_id": channel_id,
                "text": f"Error occurred: {str(e)}",
            }
        )
        raise

    finally:
        db.close()