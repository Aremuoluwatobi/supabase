from fastapi import FastAPI
from db import supabase
from contextlib import asynccontextmanager

app = FastAPI()


@app.get("/health")
def check_status():
    return {"status": "running well"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server running and connected to Supabase")
    yield
    print("server shutting down")

app = FastAPI(lifespan=lifespan)
