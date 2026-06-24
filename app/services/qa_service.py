import logging
from app.workflows.qa_graph import qa_graph
from app.database.repository import save_message

logger = logging.getLogger(__name__)


def answer_question(
    db,
    session_id,
    slack_user_id,
    channel_id,
    user_question,
):
    """
    Orchestrates QA workflow
    """
    logger.info(f"answer_question service called for session_id: {session_id}")

    logger.info("Saving user question message to database")
    save_message(db=db, session_id=session_id, role="user", content=user_question)

    logger.info("Invoking qa_graph")
    result = qa_graph.invoke(
        {
            "db": db,
            "session_id": session_id,
            "slack_user_id": slack_user_id,
            "channel_id": channel_id,
            "user_question": user_question,
        }
    )

    answer = result.get("answer", "")
    logger.info("Saving assistant answer message to database")
    save_message(db=db, session_id=session_id, role="assistant", content=answer)

    logger.info("QA workflow complete")
    return result