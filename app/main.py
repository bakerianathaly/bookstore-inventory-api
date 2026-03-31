from fastapi import FastAPI

from app.api.permissions import router as permissions_router

app = FastAPI(title="Venecare CRM")

app.include_router(permissions_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "¡Proyecto FastAPI funcionando con Docker y Postgres!"}
