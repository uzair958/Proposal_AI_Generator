import logging
from app.workflows.proposal_graph import proposal_graph
from app.database.repository import save_transcript

logger = logging.getLogger(__name__)


def generate_proposal(
    db,
    session_id,
    slack_user_id,
    channel_id,
    transcript,
):
    """
    Orchestrates proposal generation workflow
    """
    logger.info(f"generate_proposal service called for session_id: {session_id}")
    
    # Save the transcript to DB so it can be recovered/loaded in later turns
    logger.info("Saving transcript to the database")
    save_transcript(db=db, session_id=session_id, transcript_text=transcript)

    logger.info("Invoking proposal_graph")
    result = proposal_graph.invoke(
        {
            "db": db,
            "session_id": session_id,
            "slack_user_id": slack_user_id,
            "channel_id": channel_id,
            "transcript": transcript,
        }
    )
    logger.info("Proposal generation workflow invocation complete")
    return result