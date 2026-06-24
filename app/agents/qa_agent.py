import json
import logging
from app.llm.groq_client import get_llm
from app.prompts.qa_prompt import get_qa_prompt

logger = logging.getLogger(__name__)
llm = get_llm()


def qa_agent(state):
    """
    Answers questions using memory + transcript
    """
    logger.info("Starting qa_agent")

    transcript = state.get("transcript", "")
    question = state.get("user_question", "")
    messages = state.get("messages", [])
    
    # Load profile and proposal sections to answer questions about the generated/revised outputs
    client_profile = state.get("client_profile", {})
    proposal_sections = state.get("proposal_sections", {})

    formatted_profile = json.dumps(client_profile, indent=2) if client_profile else "No client profile loaded."
    formatted_proposal = json.dumps(proposal_sections, indent=2) if proposal_sections else "No proposal sections generated."

    # Format the message history list as a readable string
    formatted_messages = ""
    for msg in messages:
        role_label = "User" if msg.get("role") == "user" else "Assistant"
        formatted_messages += f"{role_label}: {msg.get('content')}\n"

    if not formatted_messages:
        formatted_messages = "No previous messages."

    # Format cross-thread memory from other sessions
    cross_thread_context = state.get("cross_thread_context", [])
    formatted_cross_thread = ""
    if cross_thread_context:
        for item in cross_thread_context:
            s_id = item.get("session_id")
            profile = item.get("client_profile")
            proposal = item.get("proposal_sections")
            formatted_cross_thread += f"--- Other Session ID {s_id} ---\n"
            if profile:
                formatted_cross_thread += f"Client Profile:\n{json.dumps(profile, indent=2)}\n"
            if proposal:
                formatted_cross_thread += f"Proposal:\n{json.dumps(proposal, indent=2)}\n"
            formatted_cross_thread += "\n"
    else:
        formatted_cross_thread = "No memory from other sessions."

    prompt = get_qa_prompt()
    chain = prompt | llm

    logger.info(f"Invoking QA chain with question: '{question}'")
    response = chain.invoke(
        {
            "transcript": transcript,
            "client_profile": formatted_profile,
            "proposal_sections": formatted_proposal,
            "messages": formatted_messages,
            "cross_thread_context": formatted_cross_thread,
            "question": question,
        }
    )

    logger.info("Successfully answered user question")
    return {
        "answer": response.content
    }
