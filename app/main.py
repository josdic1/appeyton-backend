# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel

from app.database import Base, engine
from app.routes.users import router as users_router
from app.routes.admin_users import router as admin_users_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Appeyton API", lifespan=lifespan)

app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(admin_users_router, prefix="/admin", tags=["Admin"])

class RootResponse(BaseModel):
    ok: bool
    app: str

@app.get("/", response_model=RootResponse)
def root():
    return {"ok": True, "app": "Appeyton"}
