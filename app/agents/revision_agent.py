import json
import logging
from app.llm.groq_client import get_llm
from app.prompts.revision_prompt import get_revision_prompt
from app.schemas.proposal import ProposalSections

logger = logging.getLogger(__name__)
llm = get_llm()


def revision_agent(state):
    """
    Update proposal
    """
    logger.info("Starting revision_agent")
    
    proposal = state.get("proposal_sections")
    if not proposal:
        logger.error("No proposal found in state. Memory load failed.")
        raise ValueError("No proposal found in state. Memory load failed.")
    
    revision_request = state.get("revision_request", "")
    
    revision_prompt = get_revision_prompt()
    structured_llm = llm.with_structured_output(ProposalSections)
    chain = revision_prompt | structured_llm

    # Format proposal sections nicely as a JSON string for the prompt
    formatted_proposal = json.dumps(proposal, indent=2)
    
    logger.info(f"Invoking revision chain with request: {revision_request}")
    updated_proposal = chain.invoke(
        {
            "proposal_sections": formatted_proposal,
            "revision_request": revision_request,
        }
    )

    logger.info("Revision agent successfully updated proposal sections")
    return {
        "proposal_sections": updated_proposal.model_dump()
    }