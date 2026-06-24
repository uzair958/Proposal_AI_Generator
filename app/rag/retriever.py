from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue,
)

from app.rag.embeddings import (
    get_embedding_model,
)

from app.rag.vector_store import (
    get_client,
    COLLECTION_NAME,
)


def _format_results(results):
    formatted = []

    for result in results:
        formatted.append(
            {
                "score": result.score,
                "industry": result.payload.get(
                    "industry"
                ),
                "proposal_name": result.payload.get(
                    "proposal_name"
                ),
                "text": result.payload.get(
                    "text"
                ),
            }
        )

    return formatted


def retrieve_by_problem(
    problem: str,
    limit: int = 5,
):
    client = get_client()

    embedding_model = get_embedding_model()

    query_vector = (
        embedding_model.embed_query(
            problem
        )
    )

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit,
    )

    return _format_results(results)


def retrieve_by_industry(
    industry: str,
    limit: int = 5,
):
    client = get_client()

    embedding_model = get_embedding_model()

    query_vector = (
        embedding_model.embed_query(
            industry
        )
    )

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="industry",
                    match=MatchValue(
                        value=industry.lower()
                    ),
                )
            ]
        ),
    )

    return _format_results(results)


def retrieve_context(
    industry: str,
    problem: str,
    limit_per_search: int = 5,
):
    industry_results = (
        retrieve_by_industry(
            industry=industry,
            limit=limit_per_search,
        )
    )

    problem_results = (
        retrieve_by_problem(
            problem=problem,
            limit=limit_per_search,
        )
    )

    merged = (
        industry_results
        + problem_results
    )

    deduplicated = {}

    for result in merged:

        key = (
            result["proposal_name"]
            + result["text"]
        )

        if (
            key not in deduplicated
            or result["score"]
            > deduplicated[key]["score"]
        ):
            deduplicated[key] = result

    final_results = list(
        deduplicated.values()
    )

    final_results.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    return final_results[:10]