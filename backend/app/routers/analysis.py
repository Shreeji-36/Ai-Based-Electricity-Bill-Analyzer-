from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from energy_ai import enrich
from app.data.industries import INDUSTRIES
from app.database import get_db
from app.deps import require_roles
from app.models import Analysis, Bill
from app.schemas import AnalysisIn
from app.services.energy import analyze

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("")
def run_analysis(data: AnalysisIn, user=Depends(require_roles("admin", "analyst")),
                 db: Session = Depends(get_db)):
    prior = db.scalars(select(Bill).where(Bill.user_id == user["id"],
                                          Bill.industry == data.industry)
                       .order_by(Bill.created_at)).all()
    history = [b.units for b in prior][-24:]

    result = analyze(data.industry, data.bill.model_dump(), data.hours, data.qty)
    peak = sum(m["kw"] * data.qty.get(m["id"], 1) * 0.85
               for m in INDUSTRIES[data.industry]["machines"]
               if data.hours.get(m["id"], 0) > 0)
    result["ai"] = enrich(result, history, peak)

    bill = Bill(user_id=user["id"], industry=data.industry,
                consumer_number=data.bill.consumer_number, billing_date=data.bill.billing_date,
                tariff=data.bill.tariff, units=data.bill.units,
                amount=data.bill.amount, days=data.bill.days)
    db.add(bill)
    db.flush()
    db.add(Analysis(user_id=user["id"], bill_id=bill.id, result=result))
    db.commit()
    return result