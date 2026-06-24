from pathlib import Path
import uuid

from qdrant_client.models import PointStruct

from app.rag.chunking import chunk_text
from app.rag.embeddings import get_embedding_model
from app.rag.vector_store import (
    get_client,
    COLLECTION_NAME,
    recreate_collection,
)


import logging

logger = logging.getLogger(__name__)


def detect_industry(filename: str) -> str:
    filename = filename.lower()

    industries = [
        "retail",
        "healthcare",
        "manufacturing",
        "fintech",
        "construction",
        "consulting",
        "distribution",
        "fleet",
        "logistics",
    ]

    for industry in industries:
        if industry in filename:
            return industry

    return "general"


def ingest_proposals() -> None:
    """
    Ingest all proposal examples into Qdrant.
    """

    client = get_client()  # ✅ runtime initialization

    # clear collection safely
    recreate_collection(client)

    embedding_model = get_embedding_model()

    proposal_directory = Path("data/proposals")

    if not proposal_directory.exists():
        raise FileNotFoundError(
            f"Proposal directory not found: {proposal_directory}"
        )

    total_chunks = 0

    for file_path in proposal_directory.glob("*.txt"):

        proposal_text = file_path.read_text(encoding="utf-8")
        chunks = chunk_text(proposal_text)

        if not chunks:
            continue

        vectors = embedding_model.embed_documents(chunks)

        industry = detect_industry(file_path.name)

        points = []

        for chunk, vector in zip(chunks, vectors):

            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "industry": industry,
                        "proposal_name": file_path.stem,
                        "text": chunk,
                    },
                )
            )

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
        )

        total_chunks += len(chunks)

        logger.info(f"Ingested {file_path.name} ({len(chunks)} chunks)")

    logger.info(f"Proposal ingestion complete ({total_chunks} chunks)")