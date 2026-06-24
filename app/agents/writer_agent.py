import json
import logging
from app.llm.groq_client import get_llm
from app.prompts.writer_prompt import get_writer_prompt
from app.schemas.proposal import ProposalSections

logger = logging.getLogger(__name__)
llm = get_llm()


def writer_agent(state):
    """
    Generate proposal sections
    """
    logger.info("Starting writer_agent")

    client_profile = state.get("client_profile")
    if not isinstance(client_profile, dict):
        logger.warning(f"client_profile is not a dict: {type(client_profile)}. Defaulting to empty dict.")
        client_profile = {}

    retrieved_context = state.get("retrieved_context", [])

    # Format client profile as JSON string
    formatted_profile = json.dumps(client_profile, indent=2)

    # Format retrieved context items into a clean markdown structure
    formatted_context = ""
    if retrieved_context:
        for idx, ctx in enumerate(retrieved_context, 1):
            formatted_context += f"### Example {idx} (Industry: {ctx.get('industry')}, Source: {ctx.get('proposal_name')}):\n{ctx.get('text')}\n\n"
    else:
        formatted_context = "No relevant context found."

    prompt = get_writer_prompt()
    structured_llm = llm.with_structured_output(ProposalSections)
    chain = prompt | structured_llm

    logger.info("Invoking LLM writer chain to generate proposal sections")
    proposal = chain.invoke(
        {
            "client_profile": formatted_profile,
            "retrieved_context": formatted_context,
        }
    )

    logger.info("Successfully generated proposal sections")
    return {
        "proposal_sections": proposal.model_dump()
    }