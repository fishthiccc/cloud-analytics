from fastapi import FastAPI, Depends, HTTPException, APIRouter
from app.api.v1.routers import router as metrics_router
from app.db.database import SessionLocal, engine, Base
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from app.api.tasks import weather_update

#Create the database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the background task for weather updates
    task = asyncio.create_task(weather_update())
    yield
    # Cancel the background task on shutdown
    task.cancel()


app=FastAPI(title="Cloud Analytics API", version="1.0.0",lifespan=lifespan)

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


