from fastapi import APIRouter, Depends
from app.deps import require_roles
from app.schemas import AnalysisIn
from app.services.energy import analyze

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("")
def run_analysis(data: AnalysisIn, _=Depends(require_roles("admin", "analyst"))):
    return analyze(data.industry, data.bill.model_dump(), data.hours)