from pydantic import BaseModel, Field


class ClientProfile(BaseModel):

    company_name: str | None = None

    industry: str | None = None

    problem: str | None = None

    goals: list[str] = Field(
        default_factory=list
    )

    budget: str | None = None

    timeline: str | None = None

    stakeholders: list[str] | None = None

    missing_fields: list[str] = Field(
        default_factory=list
    )