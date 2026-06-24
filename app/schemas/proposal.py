from pydantic import BaseModel


class ProposalSections(BaseModel):

    executive_summary: str

    objectives: str

    scope: str

    timeline: str

    pricing: str

    conclusion: str