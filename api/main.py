from fastapi import FastAPI

from api.routers.analysis import router as analysis_router


app = FastAPI(
    title="MOSIAC Clinical Trial Intelligence API",
    version="0.1.0",
    description="AI-powered clinical trial intelligence system.",
)

app.include_router(analysis_router)


@app.get("/")
async def root():
    return {
        "message": "MOSIAC API is running",
        "status": "ok",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
    }