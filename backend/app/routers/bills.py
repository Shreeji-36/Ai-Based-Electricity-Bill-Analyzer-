import os
import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.deps import require_roles
from app.models import Bill

router = APIRouter(prefix="/api/bills", tags=["bills"])
OCR_URL = os.getenv("OCR_URL", "http://localhost:8001")


@router.post("/upload")
async def upload(file: UploadFile = File(...), _=Depends(require_roles("admin", "analyst"))):
    data = await file.read()
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(f"{OCR_URL}/extract",
                                  files={"file": (file.filename, data, file.content_type)})
    except httpx.HTTPError:
        raise HTTPException(503, "OCR service unavailable. Please enter the bill values manually.")
    if r.status_code != 200:
        raise HTTPException(r.status_code, r.json().get("detail", "OCR failed"))
    return r.json()  # frontend shows these values for the user to confirm or edit


@router.get("")
def history(industry: str, user=Depends(require_roles("admin", "analyst", "viewer")),
            db: Session = Depends(get_db)):
    rows = db.scalars(select(Bill).where(Bill.user_id == user["id"], Bill.industry == industry)
                      .order_by(Bill.created_at.desc()).limit(24)).all()
    return [{"id": b.id, "units": b.units, "amount": b.amount,
             "billing_date": b.billing_date, "created_at": b.created_at} for b in rows]