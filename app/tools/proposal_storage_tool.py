import logging
from app.database.repository import (
    save_proposal_version,
)

logger = logging.getLogger(__name__)


def store_proposal(
    db,
    session_id: int,
    proposal: dict,
    docx_path: str | None = None,
):
    """
    Persist proposal version.
    """
    logger.info(f"Storing proposal version for session_id: {session_id}")
    return save_proposal_version(
        db=db,
        session_id=session_id,
        proposal=proposal,
        docx_path=docx_path,
    )