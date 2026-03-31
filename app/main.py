from fastapi import FastAPI

from app.api.books import router as books_router
from shared.config import DESCRIPTION, PROJECT_NAME, VERSION

app = FastAPI(title=PROJECT_NAME, description=DESCRIPTION, version=VERSION)

app.include_router(books_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": f"{PROJECT_NAME} API v{VERSION} funcionando"}
