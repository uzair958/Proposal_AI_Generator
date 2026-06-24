import logging
from app.tools.retriever_tool import (
    retrieve_proposal_context
)

logger = logging.getLogger(__name__)


def research_agent(state):
    """
    Retrieve similar proposal examples
    """
    logger.info("Starting research_agent")

    profile = state.get("client_profile")

    if not isinstance(profile, dict):
        logger.warning(f"client_profile in state is not a dict: {type(profile)}. Defaulting to empty dict.")
        profile = {}

    # Fix get() returning None if the key exists but its value is None
    industry = profile.get("industry") or "general"
    problem = profile.get("problem") or ""

    logger.info(f"Retrieving context for industry: '{industry}', problem: '{problem}'")

    retrieved_context = (
        retrieve_proposal_context.invoke(
            {
                "industry": industry,
                "problem": problem,
            }
        )
    )

    logger.info(f"Retrieved {len(retrieved_context)} context items from Qdrant")

    return {
        "retrieved_context": retrieved_context
    }