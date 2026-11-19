from fastapi import FastAPI

app = FastAPI(
    title="Document Continuity Assistant",
    description="Research prototype for organizational knowledge continuity.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "healthy"}