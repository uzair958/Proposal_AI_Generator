from langchain_core.prompts import ChatPromptTemplate


def get_revision_prompt():

    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are a proposal editing assistant.

Your job:
- Modify ONLY requested sections
- Keep all other sections unchanged
- Maintain professional tone
- Do NOT rewrite full proposal unless asked

Return updated proposal in structured format.
"""
            ),
            (
                "human",
                """
Original Proposal:
{proposal_sections}

User Request:
{revision_request}

Return updated proposal sections.
"""
            ),
        ]
    )