from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import models
from app.schemas import schemas

def create_metric(db: Session, metric: schemas.MetricCreate):
    db_metric = models.Metric(
        name = metric.name, 
        value = metric.value
    )

    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)

    return db_metric

def get_metrics(db: Session, skip: int = 0, limit: int = 100):
    stmt = select(models.Metric).offset(skip).limit(limit)
    return db.scalars(stmt).all()

def get_metric(db: Session, metric_id: int):
    stmt = select(models.Metric).where(
        models.Metric.id == metric_id
    )

    return db.scalars(stmt).first()