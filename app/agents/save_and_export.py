import logging
from app.database.repository import save_client_profile, save_proposal_version
from app.tools.docx_tool import generate_proposal_docx

logger = logging.getLogger(__name__)


def save_and_export_agent(state):
    """
    Saves client profile and proposal sections to the database,
    and exports the proposal to a DOCX file.
    """
    logger.info("Starting save_and_export_agent")
    
    db = state["db"]
    session_id = state["session_id"]
    profile = state.get("client_profile")
    proposal = state.get("proposal_sections")
    
    if profile:
        logger.info(f"Saving client profile for session_id: {session_id}")
        save_client_profile(db=db, session_id=session_id, profile=profile)
        
    docx_path = None
    if proposal:
        logger.info(f"Generating DOCX and saving proposal version for session_id: {session_id}")
        # Invoke the docx tool directly
        docx_path = generate_proposal_docx.invoke(
            {
                "proposal_sections": proposal
            }
        )
        save_proposal_version(
            db=db,
            session_id=session_id,
            proposal=proposal,
            docx_path=docx_path,
        )
        logger.info(f"Proposal saved and exported. DOCX Path: {docx_path}")
        
    return {
        "docx_path": docx_path
    }
