from langchain_core.prompts import ChatPromptTemplate


def get_intake_prompt():
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
Extract structured client data from the transcript.

Return a JSON object with:
- company_name (string or null if unknown)
- industry (string or null if unknown)
- problem (string or null if unknown)
- goals (array of strings, return [] if unknown, NEVER null)
- budget (string or null if unknown)
- timeline (string or null if unknown)
- stakeholders (array of strings, return [] if unknown, NEVER null)

IMPORTANT:
- goals and stakeholders must ALWAYS be arrays/lists. If missing or unknown, return []. Do not use null/None.
- For all other text fields, return null if unknown.
"""
            ),
            (
                "human",
                "{transcript}"
            ),
        ]
    )