from fastapi import Depends
from sqlmodel import Session

from app.db.sessions import get_db
from app.repositories.book_repository import BookRepository
from app.services.book import BookUseCase


class BookDeps:
    @staticmethod
    def get_repository(db: Session = Depends(get_db)) -> BookRepository:
        return BookRepository(db)

    @staticmethod
    def get_service(
        repo: BookRepository = Depends(get_repository),
    ) -> BookUseCase:
        return BookUseCase(repo)
