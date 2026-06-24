from typing import Dict
from typing import List
from typing import Optional
from typing import TypedDict
from typing import Any
from sqlalchemy.orm import Session

class ProposalState(TypedDict):

    db: Session

    session_id: int

    slack_user_id: str

    channel_id: str

    transcript: str

    client_profile: dict

    retrieved_context: list

    proposal_sections: dict

    revision_request: str | None

    user_question: str | None

    answer: str | None

    docx_path: str | None

    messages: list

    cross_thread_context: list

    status: str

    error: str | None