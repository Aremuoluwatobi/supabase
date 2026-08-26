from fastapi import FastAPI
from db import supabase
from fastapi import HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from fastapi import Header
from fastapi import Depends
from fastapi.security import HTTPBearer


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

security = HTTPBearer()


def get_current_user(credentials=Depends(security)):
    token = credentials.credentials

    try:
        user_details = supabase.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user_details


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
    except Exception as e:
        print(f"LOGIN ERROR: {e}")
        raise HTTPException(
            status_code=401, detail="invalid login credentials")


@app.get("/protected/profile")
def protected_profile(user=Depends(get_current_user)):
    return user


@app.get("/protected/dashboard")
def protect_dashboard(dashboard=Depends(get_current_user)):
    return dashboard


@app.post("/auth/logout", status_code=204)
def log_out(user=Depends(get_current_user), authorization: str = Header(None, alias="Authorization")):
    token = authorization[7:]

    try:
        supabase.auth.sign_out(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
