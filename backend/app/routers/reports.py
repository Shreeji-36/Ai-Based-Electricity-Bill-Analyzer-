from typing import Literal
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from app.deps import require_roles
from app.routers.analysis import _build
from app.schemas import AnalysisIn
from app.services import reports

router = APIRouter(prefix="/api/reports", tags=["reports"])

TYPES = {
    "pdf": ("application/pdf", reports.to_pdf),
    "xlsx": ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", reports.to_xlsx),
    "csv": ("text/csv", reports.to_csv),
}


@router.post("/{fmt}")
def download(fmt: Literal["pdf", "xlsx", "csv"], data: AnalysisIn,
             _=Depends(require_roles("admin", "analyst", "viewer"))):
    result = _build(data, [])  # same calculation and recommendations as the dashboard
    media, builder = TYPES[fmt]
    return Response(builder(result), media_type=media,
                    headers={"Content-Disposition": f"attachment; filename=energy-report.{fmt}"})