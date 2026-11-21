from fastapi import FastAPI

from app.core.config import settings
from app.api.routes.organizations import router as organizations_router
from app.api.routes.periods import router as periods_router
from app.api.routes.divisions import router as divisions_router
from app.api.routes.programs import router as programs_router
from app.api.routes.documents import router as documents_router
from app.api.routes.document_versions import router as document_versions_router
from app.api.routes.extracted_contents import (
    router as extracted_contents_router,
)
from app.api.routes.retrieval import router as retrieval_router

app = FastAPI(
    title=settings.app_name,
    description="Research prototype for organizational knowledge continuity.",
    version="0.1.0",
    debug=settings.debug,
)

app.include_router(organizations_router)
app.include_router(periods_router)
app.include_router(divisions_router)
app.include_router(programs_router)
app.include_router(documents_router)
app.include_router(document_versions_router)
app.include_router(extracted_contents_router)
app.include_router(retrieval_router)

@app.get("/health")
def health_check():
    return {"status": "healthy"}