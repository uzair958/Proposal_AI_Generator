from langchain_core.prompts import ChatPromptTemplate


def get_writer_prompt():
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are a senior business consultant.

Write structured professional proposals.

Rules:
- No hallucination. Use only provided context.
- Keep tone formal, concise, and clear.
- Fill out all the required sections.
"""
            ),
            (
                "human",
                """
Client Profile:
{client_profile}

Retrieved Context:
{retrieved_context}

Generate a comprehensive proposal with the following sections:
1. Executive Summary: High-level overview of the proposed solution and value proposition.
2. Objectives: The key goals and business outcomes of this project.
3. Scope: What is included (and excluded) in this engagement.
4. Timeline: Implementation phases, key milestones, and duration.
5. Pricing: Detailed budget, cost breakdown, and payment structure.
6. Conclusion: Wrap up and next steps.
"""
            ),
        ]
    )