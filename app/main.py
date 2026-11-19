from fastapi import FastAPI

from app.core.config import settings
from app.api.routes.organizations import router as organizations_router
from app.api.routes.periods import router as periods_router

app = FastAPI(
    title=settings.app_name,
    description="Research prototype for organizational knowledge continuity.",
    version="0.1.0",
    debug=settings.debug,
)

app.include_router(organizations_router)
app.include_router(periods_router)

@app.get("/health")
def health_check():
    return {"status": "healthy"}