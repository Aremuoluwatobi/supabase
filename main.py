from fastapi import FastAPI
from db import supabase
from fastapi import HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from fastapi import Header

app = FastAPI()


class AuthRequest(BaseModel):
    email: str
    password: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server running and connected to Supabase")
    yield
    print("server shutting down")

app = FastAPI(lifespan=lifespan)


@app.get("/health")
def check_status():
    return {"status": "running well"}


@app.get("/public/info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}


@app.post("/auth/signup", status_code=201)
def create_login(request: AuthRequest):
    if not request.email or not request.password:
        raise HTTPException(status_code=400, detail="invalid cridentials")

    result = supabase.auth.sign_up({
        "email": request.email,
        "password": request.password
    })
    return result


@app.post("/auth/login")
def check_login(request: AuthRequest):
    if not request.email or not request.password:
        raise HTTPException(status_code=400, detail="need email and passowrd")
    try:
        result = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        return result
    except Exception:
        raise HTTPException(
            status_code=401, detail="invalid login credentials")


@app.get("/protected/profile")
def protected_profile(authorization: str = Header(None, alias="Authorization")):
    print(f"Received:[{authorization}]")
    if not authorization:
        raise HTTPException(status_code=401, detail="Access token required")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Access token required")
    else:
        return {"message": "token looks valid, not yet verified"}
