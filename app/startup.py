import logging
from app.rag.ingestion import ingest_proposals
from app.database.base import Base
from app.database.connection import engine

# force model registration
from app.database.models import *
Base.metadata.create_all(bind=engine)

logger = logging.getLogger(__name__)

def startup_tasks():
    """
    Runs on application startup.
    """
    logger.info("Running startup tasks...")
    ingest_proposals()
    logger.info("Startup complete")