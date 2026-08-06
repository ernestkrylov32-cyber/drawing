from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import Optional
from database import get_db
from auth import require_auth

router = APIRouter()
MAX_IMAGE_LEN = 10 * 1024 * 1024

class DrawingCreate(BaseModel):
    title: Optional[str] = None
    image_data: str = Field(..., min_length=100)

@router.get("/api/drawings")
async def list_drawings(user=Depends(require_auth)):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, title, created_at FROM drawings WHERE user_id = ? ORDER BY created_at DESC", (user["id"],))
    rows = cur.fetchall()
    conn.close()
    return {"drawings": [dict(r) for r in rows]}

@router.get("/api/drawings/{drawing_id}")
async def get_drawing(drawing_id: int, user=Depends(require_auth)):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, title, image_data, created_at FROM drawings WHERE id = ? AND user_id = ?", (drawing_id, user["id"]))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Рисунок не найден")
    return {"drawing": dict(row)}

@router.post("/api/drawings")
async def create_drawing(body: DrawingCreate, user=Depends(require_auth)):
    if not body.image_data.startswith("data:image/"):
        raise HTTPException(status_code=400, detail="Некорректные данные изображения")
    if len(body.image_data) > MAX_IMAGE_LEN:
        raise HTTPException(status_code=413, detail="Изображение слишком большое")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO drawings (user_id, title, image_data) VALUES (?, ?, ?)",
                (user["id"], body.title, body.image_data))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return {"id": new_id}

@router.delete("/api/drawings/{drawing_id}")
async def delete_drawing(drawing_id: int, user=Depends(require_auth)):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM drawings WHERE id = ? AND user_id = ?", (drawing_id, user["id"]))
    conn.commit()
    changed = cur.rowcount
    conn.close()
    if changed == 0:
        raise HTTPException(status_code=404, detail="Рисунок не найден")
    return {"ok": True}
