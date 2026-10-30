import asyncio
import os
from fastapi import FastAPI

app = FastAPI()

DELAY_S = float(os.environ.get("AGELGIL_MOCK_SLM_DELAY_S", "0.2"))


@app.post("/api/generate")
async def generate(req: dict) -> dict:
    await asyncio.sleep(DELAY_S)
    mid = req.get("misconception_id", "unknown")
    return {
        "response": f"[mock-hint for {mid}] Re-check the sign of the velocity in your simulation.",
        "done": True
    }
