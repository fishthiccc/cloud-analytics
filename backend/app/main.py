from fastapi import FastAPI, Depends, HTTPException, APIRouter
from app.api.v1.routers import router as metrics_router
from app.db.database import SessionLocal, engine, Base
from fastapi.middleware.cors import CORSMiddleware

#Create the database tables
Base.metadata.create_all(bind=engine)

app=FastAPI(title="Cloud Analytics API", version="1.0.0")

#CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(metrics_router)


@app.get("/")
def root():
    return {"message": "Welcome to the Cloud Analytics API!"}


