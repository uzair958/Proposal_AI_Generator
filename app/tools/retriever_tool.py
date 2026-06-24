from langchain.tools import tool
from app.rag.retriever import retrieve_context


@tool
def retrieve_proposal_context(industry: str, problem: str):
    """
    Semantic retrieval from Qdrant
    """

    return retrieve_context(
        industry=industry,
        problem=problem,
    )