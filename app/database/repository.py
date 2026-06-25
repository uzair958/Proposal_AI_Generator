import json
import logging
from sqlalchemy.orm import Session

from app.database.models import (
    Session as SessionModel,
    Transcript,
    ProposalVersion,
    Message,
)

logger = logging.getLogger(__name__)


# ==================================================
# SESSION OPERATIONS
# ==================================================

def get_or_create_session(
    db: Session,
    slack_user_id: str,
):
    logger.info(f"get_or_create_session called with slack_user_id: '{slack_user_id}'")
    session = (
        db.query(SessionModel)
        .filter(
            SessionModel.slack_user_id == slack_user_id
        )
        .first()
    )

    if session:
        logger.info(f"Found existing database session with ID: {session.id}")
        return session

    logger.info(f"No session found. Creating a new session for slack_user_id: '{slack_user_id}'")
    session = SessionModel(
        slack_user_id=slack_user_id
    )

    db.add(session)
    db.commit()
    db.refresh(session)
    logger.info(f"Successfully created database session with ID: {session.id}")

    return session


# ==================================================
# TRANSCRIPT OPERATIONS
# ==================================================

def save_transcript(
    db: Session,
    session_id: int,
    transcript_text: str,
):
    logger.info(f"save_transcript called for session_id: {session_id}")
    transcript = Transcript(
        session_id=session_id,
        content=transcript_text,
    )

    db.add(transcript)
    db.commit()
    db.refresh(transcript)
    logger.info(f"Successfully saved transcript (ID: {transcript.id}) for session_id: {session_id}")

    return transcript


def get_latest_transcript(
    db: Session,
    session_id: int,
):
    logger.info(f"get_latest_transcript called for session_id: {session_id}")
    return (
        db.query(Transcript)
        .filter(
            Transcript.session_id == session_id
        )
        .order_by(
            Transcript.uploaded_at.desc()
        )
        .first()
    )


# ==================================================
# PROPOSAL OPERATIONS
# ==================================================

def save_proposal_version(
    db: Session,
    session_id: int,
    proposal: dict,
    docx_path: str | None = None,
):
    logger.info(f"save_proposal_version called for session_id: {session_id}")
    latest = (
        db.query(ProposalVersion)
        .filter(
            ProposalVersion.session_id == session_id
        )
        .order_by(
            ProposalVersion.version.desc()
        )
        .first()
    )

    version = 1

    if latest:
        version = latest.version + 1
        logger.info(f"Previous proposal version found: v{latest.version}. New version will be: v{version}")
    else:
        logger.info("No previous proposal version found. Initializing as v1.")

    proposal_version = ProposalVersion(
        session_id=session_id,
        version=version,
        proposal_json=json.dumps(proposal),
        docx_path=docx_path,
    )

    db.add(proposal_version)
    db.commit()
    db.refresh(proposal_version)
    logger.info(f"Successfully saved proposal version v{version} (ID: {proposal_version.id}) for session_id: {session_id}")

    return proposal_version


def get_latest_proposal(
    db: Session,
    session_id: int,
):
    logger.info(f"get_latest_proposal called for session_id: {session_id}")
    latest = (
        db.query(ProposalVersion)
        .filter(
            ProposalVersion.session_id == session_id
        )
        .order_by(
            ProposalVersion.version.desc()
        )
        .first()
    )

    if not latest:
        logger.info(f"No proposal versions found for session_id: {session_id}")
        return None

    logger.info(f"Retrieved latest proposal version: v{latest.version}")
    return json.loads(
        latest.proposal_json
    )


def get_proposal_version(
    db: Session,
    session_id: int,
    version: int,
):
    logger.info(f"get_proposal_version called for session_id: {session_id}, version: {version}")
    proposal = (
        db.query(ProposalVersion)
        .filter(
            ProposalVersion.session_id == session_id,
            ProposalVersion.version == version,
        )
        .first()
    )

    if not proposal:
        logger.info(f"Proposal version v{version} not found for session_id: {session_id}")
        return None

    logger.info(f"Retrieved proposal version v{version} for session_id: {session_id}")
    return json.loads(
        proposal.proposal_json
    )


# ==================================================
# MESSAGE OPERATIONS
# ==================================================

def save_message(
    db: Session,
    session_id: int,
    role: str,
    content: str,
):
    logger.info(f"save_message called for session_id: {session_id}, role: {role}")
    message = Message(
        session_id=session_id,
        role=role,
        content=content,
    )

    db.add(message)
    db.commit()
    db.refresh(message)
    logger.info(f"Successfully saved message (ID: {message.id}) for session_id: {session_id}")

    return message


def get_messages(
    db: Session,
    session_id: int,
):
    logger.info(f"get_messages called for session_id: {session_id}")
    return (
        db.query(Message)
        .filter(
            Message.session_id == session_id
        )
        .order_by(
            Message.created_at.asc()
        )
        .all()
    )


# ==================================================
# CLIENT PROFILE OPERATIONS
# ==================================================

def save_client_profile(
    db: Session,
    session_id: int,
    profile: dict,
):
    logger.info(f"save_client_profile called for session_id: {session_id}")
    from app.database.models import ClientProfile

    existing = (
        db.query(ClientProfile)
        .filter(
            ClientProfile.session_id == session_id
        )
        .first()
    )

    if existing:
        logger.info(f"Found existing client profile for session_id: {session_id}. Updating it.")

        existing.company_name = profile.get(
            "company_name"
        )

        existing.industry = profile.get(
            "industry"
        )

        existing.problem = profile.get(
            "problem"
        )

        existing.goals = json.dumps(
            profile.get("goals", [])
        )

        existing.budget = profile.get(
            "budget"
        )

        existing.timeline = profile.get(
            "timeline"
        )

        existing.stakeholders = json.dumps(
            profile.get("stakeholders", [])
        )

        existing.missing_fields = json.dumps(
            profile.get("missing_fields", [])
        )

        db.commit()
        db.refresh(existing)
        logger.info(f"Successfully updated client profile (ID: {existing.id}) for session_id: {session_id}")

        return existing

    logger.info(f"No client profile found for session_id: {session_id}. Creating new client profile.")
    client_profile = ClientProfile(
        session_id=session_id,
        company_name=profile.get(
            "company_name"
        ),
        industry=profile.get(
            "industry"
        ),
        problem=profile.get(
            "problem"
        ),
        goals=json.dumps(
            profile.get("goals", [])
        ),
        budget=profile.get(
            "budget"
        ),
        timeline=profile.get(
            "timeline"
        ),
        stakeholders=json.dumps(
            profile.get("stakeholders", [])
        ),
        missing_fields=json.dumps(
            profile.get("missing_fields", [])
        ),
    )

    db.add(client_profile)
    db.commit()
    db.refresh(client_profile)
    logger.info(f"Successfully created client profile (ID: {client_profile.id}) for session_id: {session_id}")

    return client_profile


def get_client_profile(
    db: Session,
    session_id: int,
):
    logger.info(f"get_client_profile called for session_id: {session_id}")
    from app.database.models import ClientProfile

    profile = (
        db.query(ClientProfile)
        .filter(
            ClientProfile.session_id == session_id
        )
        .first()
    )

    if not profile:
        logger.info(f"No client profile found for session_id: {session_id}")
        return None

    logger.info(f"Retrieved client profile (ID: {profile.id}) for session_id: {session_id}")
    return {
        "company_name": profile.company_name,
        "industry": profile.industry,
        "problem": profile.problem,
        "goals": json.loads(
            profile.goals or "[]"
        ),
        "budget": profile.budget,
        "timeline": profile.timeline,
        "stakeholders": json.loads(
            profile.stakeholders or "[]"
        ),
        "missing_fields": json.loads(
            profile.missing_fields or "[]"
        ),
    }


# ==================================================
# CROSS THREAD MEMORY OPERATIONS
# ==================================================

def get_cross_thread_memory(
    db: Session,
    session_id: int,
    slack_user_id: str,
):
    logger.info(f"get_cross_thread_memory called for session_id: {session_id}, slack_user_id: '{slack_user_id}'")
    
    # Parse base user ID (e.g. "U12345" from "U12345:C99999")
    base_user_id = slack_user_id.split(":")[0] if ":" in slack_user_id else slack_user_id
    
    # Find all sessions belonging to this base user (excluding the current one)
    other_sessions = (
        db.query(SessionModel)
        .filter(
            (SessionModel.slack_user_id == base_user_id) |
            (SessionModel.slack_user_id.like(f"{base_user_id}:%"))
        )
        .filter(SessionModel.id != session_id)
        .all()
    )
    
    logger.info(f"Found {len(other_sessions)} other sessions for base user: '{base_user_id}'")
    
    cross_memory = []
    for s in other_sessions:
        proposal = get_latest_proposal(db, s.id)
        profile = get_client_profile(db, s.id)
        if proposal or profile:
            cross_memory.append({
                "session_id": s.id,
                "client_profile": profile,
                "proposal_sections": proposal
            })
            
    return cross_memory


def get_all_sessions_for_user(
    db: Session,
    slack_user_id: str,
):
    logger.info(f"get_all_sessions_for_user called for slack_user_id: '{slack_user_id}'")
    base_user_id = slack_user_id.split(":")[0] if ":" in slack_user_id else slack_user_id
    return (
        db.query(SessionModel)
        .filter(
            (SessionModel.slack_user_id == base_user_id) |
            (SessionModel.slack_user_id.like(f"{base_user_id}:%"))
        )
        .order_by(SessionModel.created_at.desc())
        .all()
    )


def get_latest_proposal_record(
    db: Session,
    session_id: int,
):
    logger.info(f"get_latest_proposal_record called for session_id: {session_id}")
    return (
        db.query(ProposalVersion)
        .filter(
            ProposalVersion.session_id == session_id
        )
        .order_by(
            ProposalVersion.version.desc()
        )
        .first()
    )


def delete_session(
    db: Session,
    session_id: int,
):
    logger.info(f"delete_session called for session_id: {session_id}")
    # Import locally to avoid potential circular dependencies
    from app.database.models import ClientProfile

    # Delete dependent entities first
    db.query(Transcript).filter(Transcript.session_id == session_id).delete()
    db.query(ProposalVersion).filter(ProposalVersion.session_id == session_id).delete()
    db.query(Message).filter(Message.session_id == session_id).delete()
    db.query(ClientProfile).filter(ClientProfile.session_id == session_id).delete()
    
    # Delete the session itself
    db.query(SessionModel).filter(SessionModel.id == session_id).delete()
    db.commit()
    logger.info(f"Successfully deleted session: {session_id} and all related entities")


