from fastapi import APIRouter, HTTPException
from app.data.industries import INDUSTRIES

router = APIRouter(prefix="/api/industries", tags=["industries"])


@router.get("")
def list_industries():
    return [{"id": k, "name": v["name"]} for k, v in INDUSTRIES.items()]


@router.get("/{industry_id}/machines")
def machines(industry_id: str):
    ind = INDUSTRIES.get(industry_id)
    if not ind:
        raise HTTPException(404, "Industry not found")
    return {"rate": ind["rate"], "machines": ind["machines"]}