from langchain_core.prompts import ChatPromptTemplate


def get_qa_prompt():
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You answer consultant questions using the provided context:
- transcript (initial client conversation)
- client profile (initial extracted details)
- current proposal sections (the latest, active proposal)
- conversation history
- cross-thread memory (history/proposals from other sessions for this client/consultant)

IMPORTANT:
- The current proposal sections represent the latest authoritative details, which may have been revised or customized by the consultant after the initial intake. 
- If there is a difference between the initial transcript/client profile and the current proposal sections, the current proposal sections represent the revised, updated, and active version of the proposal.
- Use the cross-thread memory to reference prior context, client preferences, or historical proposal details from other sessions if the user asks about them or if they help answer the question.
- Never hallucinate missing details. If unknown, say clearly.
"""
            ),
            (
                "human",
                """
Transcript:
{transcript}

Client Profile:
{client_profile}

Current Proposal Sections:
{proposal_sections}

Cross-Thread Memory:
{cross_thread_context}

Conversation:
{messages}

Question:
{question}
"""
            ),
        ]
    )
