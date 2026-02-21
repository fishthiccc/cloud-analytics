from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.schemas import MetricOut, MetricCreate
from app.services.metrics import (
    get_metrics,
    create_metric,
    get_metric
)

from app.db.deps import get_db


router = APIRouter(
    prefix="/api/v1/metrics",
    tags=["metrics"]
    )


@router.get("/health")
def health():
    return {"status": "ok"}

# Get all metrics 
@router.get("/", response_model = list[MetricOut])
def read_metrics(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return get_metrics(db, skip, limit)


# Create Metric
@router.post("/", response_model = MetricOut)
def create_metric_endpoint(
    metric: MetricCreate, 
    db: Session = Depends(get_db)
):
    return create_metric(db, metric)


# Get one metric
@router.get("/{metric_id}", response_model = MetricOut)
def read_metric(
    metric_id: int, 
    db: Session = Depends(get_db)
):
    metric = get_metric(db, metric_id)

    if metric is None:
        raise HTTPException(status_code=404, detail="Metric not found")
    
    return metric


