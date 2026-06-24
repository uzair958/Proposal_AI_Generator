import logging
from app.database.repository import (
    get_latest_proposal,
    get_client_profile,
    get_messages,
    get_latest_transcript,
    get_cross_thread_memory,
)

logger = logging.getLogger(__name__)


def load_memory_agent(state):
    """
    Load previous session memory from database into graph state.
    """
    logger.info("Starting load_memory_agent")
    
    db = state["db"]
    session_id = state["session_id"]
    slack_user_id = state.get("slack_user_id") or ""
    
    logger.info(f"Retrieving memory for session_id: {session_id}, slack_user_id: {slack_user_id}")

    proposal = get_latest_proposal(
        db=db,
        session_id=session_id,
    )

    profile = get_client_profile(
        db=db,
        session_id=session_id,
    )

    messages = get_messages(
        db=db,
        session_id=session_id,
    )

    transcript_record = get_latest_transcript(
        db=db,
        session_id=session_id,
    )

    cross_thread_context = []
    if slack_user_id:
        try:
            cross_thread_context = get_cross_thread_memory(
                db=db,
                session_id=session_id,
                slack_user_id=slack_user_id,
            )
            logger.info(f"Loaded {len(cross_thread_context)} cross-thread sessions")
        except Exception as e:
            logger.error(f"Error loading cross-thread memory: {e}", exc_info=True)

    updates = {}
    
    if proposal is not None:
        logger.info("Found existing proposal in database; loading into state")
        updates["proposal_sections"] = proposal
    else:
        logger.info("No existing proposal found in database")

    if profile is not None:
        logger.info("Found existing client profile in database; loading into state")
        updates["client_profile"] = profile
    else:
        logger.info("No existing client profile found in database")

    if transcript_record is not None:
        logger.info("Found existing transcript in database; loading into state")
        updates["transcript"] = transcript_record.content
    else:
        logger.info("No existing transcript found in database")

    formatted_messages = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in messages
    ]

    logger.info(f"Loaded {len(formatted_messages)} past messages from database")
    updates["messages"] = formatted_messages
    updates["cross_thread_context"] = cross_thread_context

    return updates