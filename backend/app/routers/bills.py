import asyncio
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


async def _call_ocr(data: bytes, filename: str, content_type: str | None) -> httpx.Response:
    """Calls the OCR service; retries a couple of times while a free server is still waking up."""
    r = None
    for attempt in range(3):
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(f"{OCR_URL.rstrip('/')}/extract",
                                  files={"file": (filename, data, content_type)})
        if r.status_code not in (502, 503, 504):
            break
        if attempt < 2:
            await asyncio.sleep(12)
    return r


@router.get("/ocr-status")
async def ocr_status():
    """Open this in the browser to see exactly why OCR is not working."""
    url = OCR_URL.rstrip("/") + "/health"
    info: dict = {"ocr_url_is_set": bool(os.getenv("OCR_URL")), "ocr_url": OCR_URL, "checked": url}
    if not os.getenv("OCR_URL"):
        info["verdict"] = ("OCR_URL is NOT set on this backend, so it is trying localhost. "
                           "Add OCR_URL in Render > backend service > Environment.")
        return info
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            r = await client.get(url)
    except httpx.HTTPError as e:
        info["error"] = type(e).__name__
        info["verdict"] = ("Cannot connect to OCR_URL. Check it is exactly https://<name>.onrender.com "
                           "(https at the start, no / at the end, no spelling mistakes).")
        return info
    info["status_code"] = r.status_code
    info["reply"] = r.text[:200]
    if r.status_code == 200:
        info["verdict"] = "OK: the OCR service is running."
    elif r.status_code in (502, 503, 504):
        info["verdict"] = ("The OCR service exists but is NOT running (crashed, failed deploy, or suspended). "
                           "Open Render > OCR service > Logs to see why.")
    elif r.status_code == 404:
        info["verdict"] = ("The address answered 404. OCR_URL points to the wrong service or the OCR "
                           "service was never deployed as a Docker web service.")
    else:
        info["verdict"] = f"Unexpected status {r.status_code}. Check the OCR service logs."
    return info


@router.post("/upload")
async def upload(file: UploadFile = File(...), _=Depends(require_roles("admin", "analyst"))):
    data = await file.read()
    try:
        r = await _call_ocr(data, file.filename, file.content_type)
    except httpx.HTTPError:
        raise HTTPException(503, "OCR service unavailable. Please try again in a minute, "
                                 "or enter the bill values manually.")
    if r.status_code in (502, 503, 504):
        raise HTTPException(503, "The OCR service is not responding (it may still be waking up, or it may be "
                                 "down). Please try again in a minute, or enter the values manually. "
                                 "Site admin: open /api/bills/ocr-status on the backend to see why.")
    try:
        body = r.json()
    except ValueError:
        raise HTTPException(502, "The OCR service sent an unexpected reply. "
                                 "Please try again or enter the bill values manually.")
    if r.status_code != 200:
        detail = body.get("detail") if isinstance(body, dict) else None
        raise HTTPException(r.status_code if r.status_code < 500 else 502,
                            detail if isinstance(detail, str) else "OCR failed")
    return body  # frontend shows these values for the user to confirm or edit


@router.get("")
def history(industry: str, user=Depends(require_roles("admin", "analyst", "viewer")),
            db: Session = Depends(get_db)):
    rows = db.scalars(select(Bill).where(Bill.user_id == user["id"], Bill.industry == industry)
                      .order_by(Bill.created_at.desc()).limit(24)).all()
    return [{"id": b.id, "units": b.units, "amount": b.amount,
             "billing_date": b.billing_date, "created_at": b.created_at} for b in rows]