from qdrant_client import QdrantClient

from qdrant_client.models import (
    Distance,
    VectorParams,
    PayloadSchemaType,
)

from app.config.settings import settings


COLLECTION_NAME = "proposal_chunks"


def get_client():
    return QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY or None,
        check_compatibility=False,
    )


def create_collection(client):
    collections = client.get_collections()

    existing = {
        c.name
        for c in collections.collections
    }

    if COLLECTION_NAME in existing:
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE,
        ),
    )

    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="industry",
        field_schema=PayloadSchemaType.KEYWORD,
    )


def recreate_collection(client):
    collections = client.get_collections()

    existing = {
        c.name
        for c in collections.collections
    }

    if COLLECTION_NAME in existing:
        client.delete_collection(
            collection_name=COLLECTION_NAME
        )

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE,
        ),
    )

    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="industry",
        field_schema=PayloadSchemaType.KEYWORD,
    )