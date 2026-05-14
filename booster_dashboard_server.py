from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import booster_logic
from pydantic import BaseModel
import os

app = FastAPI()

class BoostRequest(BaseModel):
    token: str
    invite: str

# Serve static files from the dashboard directory
app.mount("/static", StaticFiles(directory="dashboard"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("dashboard/index.html")

@app.get("/style.css")
async def read_css():
    return FileResponse("dashboard/style.css")

@app.get("/script.js")
async def read_js():
    return FileResponse("dashboard/script.js")

@app.post("/api/boost")
async def api_boost(request: BoostRequest):
    result = await booster_logic.boost_with_token(request.token, request.invite)
    return result

if __name__ == "__main__":
    print("🚀 Antigravity Booster Dashboard starting on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
