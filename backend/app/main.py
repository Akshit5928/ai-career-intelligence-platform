from fastapi import FastAPI

from backend.app.api import router as career_router

app = FastAPI(
    title="AI Career Intelligence Platform",
    version="0.2.0",
)

app.include_router(career_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
