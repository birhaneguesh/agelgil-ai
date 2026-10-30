import os
import httpx
from fastapi import FastAPI, HTTPException

app = FastAPI()

MOCK_SLM_URL = os.environ.get("AGELGIL_MOCK_SLM_URL", "http://localhost:11434")


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.post("/api/v1/hint")
async def hint(req: dict) -> dict:
    mid = req.get("misconception_id")
    if not mid:
        raise HTTPException(status_code=400, detail="misconception_id required")
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(f"{MOCK_SLM_URL}/api/generate", json={"misconception_id": mid})
        r.raise_for_status()
        data = r.json()
    return {"hint": data["response"], "source": "mock-slm"}
