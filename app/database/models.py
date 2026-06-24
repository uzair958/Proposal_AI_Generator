from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from sqlalchemy.sql import func

from app.database.base import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    slack_user_id = Column(
        String,
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(
        Integer,
        primary_key=True,
    )

    session_id = Column(
        Integer,
        ForeignKey("sessions.id"),
        nullable=False,
    )

    content = Column(
        Text,
        nullable=False,
    )

    uploaded_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class ClientProfile(Base):
    __tablename__ = "client_profiles"

    id = Column(
        Integer,
        primary_key=True,
    )

    session_id = Column(
        Integer,
        ForeignKey("sessions.id"),
        nullable=False,
    )

    company_name = Column(String)

    industry = Column(String)

    problem = Column(Text)

    goals = Column(Text)

    budget = Column(String)

    timeline = Column(String)

    stakeholders = Column(Text)

    missing_fields = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class ProposalVersion(Base):
    __tablename__ = "proposal_versions"

    id = Column(
        Integer,
        primary_key=True,
    )

    session_id = Column(
        Integer,
        ForeignKey("sessions.id"),
        nullable=False,
    )

    version = Column(
        Integer,
        nullable=False,
    )

    proposal_json = Column(
        Text,
        nullable=False,
    )

    docx_path = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(
        Integer,
        primary_key=True,
    )

    session_id = Column(
        Integer,
        ForeignKey("sessions.id"),
        nullable=False,
    )

    role = Column(
        String,
        nullable=False,
    )

    content = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )