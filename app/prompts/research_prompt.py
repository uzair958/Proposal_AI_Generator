from langchain_core.prompts import ChatPromptTemplate


def get_research_prompt():

    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You retrieve relevant proposal examples.

Focus on similarity in:
- industry
- problem type
"""
            ),
            (
                "human",
                """
Industry: {industry}
Problem: {problem}
"""
            ),
        ]
    )