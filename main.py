import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from database import init_db
from routes import auth as auth_routes
from routes import drawings as drawings_routes

init_db()

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Онлайн-рисовалка")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(drawings_routes.router)

static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/healthz")
async def healthz():
    return {"ok": True}

@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    return FileResponse(static_path / "index.html")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
