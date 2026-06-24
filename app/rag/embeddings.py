from functools import lru_cache

from langchain_community.embeddings import (
    HuggingFaceEmbeddings,
)

from app.config.settings import settings


@lru_cache
def get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL
    )