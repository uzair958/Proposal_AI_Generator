import logging
from app.llm.groq_client import get_llm
from app.prompts.intake_prompt import get_intake_prompt
from app.schemas.client_profile import ClientProfile

logger = logging.getLogger(__name__)
llm = get_llm()


def intake_agent(state):
    """
    Extract structured client information
    """
    logger.info("Starting intake_agent")
    
    transcript = state.get("transcript", "")
    logger.info(f"Received transcript with length: {len(transcript)} characters")

    prompt = get_intake_prompt()

    structured_llm = (
        llm.with_structured_output(
            ClientProfile
        )
    )

    chain = prompt | structured_llm

    logger.info("Invoking LLM for structured client profile extraction")
    profile = chain.invoke(
        {
            "transcript": transcript
        }
    )

    profile_dict = profile.model_dump()
    logger.info(f"Successfully extracted client profile for: {profile_dict.get('company_name')}")
    
    return {
        "client_profile": profile_dict
    }