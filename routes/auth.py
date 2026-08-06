from fastapi import APIRouter, Request, Response, HTTPException, status, Depends
from pydantic import BaseModel, Field
import re
from database import get_db
from auth import hash_password, verify_password, create_token, require_auth

router = APIRouter()

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_\-\u0400-\u04FF]{3,20}$")

class AuthBody(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=6)

@router.post("/api/auth/register")
async def register(body: AuthBody, response: Response):
    if not USERNAME_RE.match(body.username):
        raise HTTPException(status_code=400, detail="Логин: 3-20 символов, буквы/цифры/_/-")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username = ?", (body.username,))
    if cur.fetchone():
        conn.close()
        raise HTTPException(status_code=409, detail="Такой логин уже занят")
    pw_hash = hash_password(body.password)
    cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (body.username, pw_hash))
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    token = create_token(user_id, body.username)
    response.set_cookie(key="token", value=token, httponly=True, samesite="lax", max_age=30*24*60*60)
    return {"user": {"id": user_id, "username": body.username}}

@router.post("/api/auth/login")
async def login(body: AuthBody, response: Response):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (body.username,))
    row = cur.fetchone()
    conn.close()
    if not row or not verify_password(body.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    token = create_token(row["id"], row["username"])
    response.set_cookie(key="token", value=token, httponly=True, samesite="lax", max_age=30*24*60*60)
    return {"user": {"id": row["id"], "username": row["username"]}}

@router.post("/api/auth/logout")
async def logout(response: Response):
    response.delete_cookie(key="token")
    return {"ok": True}

@router.get("/api/auth/me")
async def me(request: Request, user=Depends(require_auth)):
    return {"user": user}
