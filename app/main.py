from fastapi import FastAPI

from app.startup import startup_tasks
from app.slack.events import router as slack_router
from app.config.logging import setup_logging

app = FastAPI(title="Proposal Generator AI")

logger = setup_logging()


@app.on_event("startup")
async def startup_event():
    logger.info("System starting...")

    startup_tasks()


# Slack routes
app.include_router(
    slack_router,
    prefix="/slack",
    tags=["Slack"],
)


@app.get("/")
def health_check():
    return {"status": "running"}