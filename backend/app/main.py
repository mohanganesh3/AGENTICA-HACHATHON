# backend/app/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from .database import init_db
from .routes import documents, chat, users
from .auth import get_current_user

app = FastAPI(title="Healthcare Document Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    await init_db()

app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(
    documents.router, 
    prefix="/api/documents", 
    tags=["documents"],
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    chat.router, 
    prefix="/api/chat", 
    tags=["chat"],
    dependencies=[Depends(get_current_user)]
)

@app.get("/api/health")
async def health():
    return {"status": "healthy"}