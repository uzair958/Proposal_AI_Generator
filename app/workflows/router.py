import logging
from langchain_core.prompts import (
    ChatPromptTemplate,
)

from app.llm.groq_client import (
    get_llm,
)

logger = logging.getLogger(__name__)
llm = get_llm()

def classify_request(
    user_message: str,
):
    logger.info("Starting request classification")
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
Classify request into one category:

proposal_generation
revision
question

Return category only.
"""
            ),
            (
                "human",
                "{message}"
            ),
        ]
    )

    chain = prompt | llm

    logger.info(f"Invoking LLM for request classification on user message: '{user_message[:50]}...'")
    response = chain.invoke(
        {
            "message": user_message
        }
    )

    category = (
        response.content
        .strip()
        .lower()
    )
    logger.info(f"Classified request category as: '{category}'")
    return category