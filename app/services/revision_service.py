import logging
from app.workflows.revision_graph import revision_graph
from app.database.repository import save_message

logger = logging.getLogger(__name__)


def revise_proposal(
    db,
    session_id,
    slack_user_id,
    channel_id,
    revision_request,
):
    """
    Orchestrates revision workflow
    """
    logger.info(f"revise_proposal service called for session_id: {session_id}")

    # Save revision request to message history for better QA context
    logger.info("Saving revision request message to database")
    save_message(
        db=db,
        session_id=session_id,
        role="user",
        content=f"Revision Request: {revision_request}"
    )

    logger.info("Invoking revision_graph")
    result = revision_graph.invoke(
        {
            "db": db,
            "session_id": session_id,
            "slack_user_id": slack_user_id,
            "channel_id": channel_id,
            "revision_request": revision_request,
        }
    )
    
    logger.info("Saving revision confirmation message to database")
    save_message(
        db=db,
        session_id=session_id,
        role="assistant",
        content="Proposal revised successfully."
    )

    logger.info("Revision workflow invocation complete")
    return result
