from fastapi import FastAPI

from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    description="Research prototype for organizational knowledge continuity.",
    version="0.1.0",
    debug=settings.debug,
)


@app.get("/health")
def health_check():
    return {"status": "healthy"}