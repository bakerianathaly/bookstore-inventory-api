from typing import Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import BookListEmptyException
from app.models.book import Book


class BookRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, book: Book) -> Book:
        try:
            self.db.add(book)
            await self.db.commit()
            await self.db.refresh(book)
            return book
        except Exception as e:
            await self.db.rollback()
            raise Exception(f"Error al crear libro: {e!s}") from e

    async def get_by_id(self, book_id: int) -> Optional[Book]:
        statement = select(Book).where(Book.id == book_id)
        result = await self.db.exec(statement)
        return result.one_or_none()

    async def get_by_isbn(self, isbn: str) -> Optional[Book]:
        statement = select(Book).where(Book.isbn == isbn)
        result = await self.db.exec(statement)
        return result.one_or_none()
        
    async def get_by_title(self, title: str) -> Optional[Book]:
        statement = select(Book).where(Book.title == title)
        result = await self.db.exec(statement)
        return result.one_or_none()

    async def get_all_paginated(
        self, page: int = 1, limit: int = 10
    ) -> Tuple[list[dict], int]:
        offset = (page - 1) * limit

        count_statement = select(func.count()).select_from(Book)
        count_result = await self.db.exec(count_statement)
        total_records = count_result.one_or_none()
        
        # Si no hay ningun libro en BD (la paginacion es 0) regreso el estatus 204 No Content (Sin Contenido)
        if total_records == 0  or total_records is None:
            raise BookListEmptyException('El listado de los libros se encuentra vacio')

        query = select(Book).order_by(Book.title).offset(offset).limit(limit)
        result = await self.db.exec(query)
        books = list(result.all())
        books = [dict(x._mapping) for x in books]

        return books, total_records

    async def search_by_category(
        self, category: str, page: int = 1, limit: int = 10
    ) -> Tuple[list[Book], int]:
        offset = (page - 1) * limit

        count_statement = (
            select(func.count())
            .select_from(Book)
            .where(Book.category.ilike(f"%{category}%"))
        )
        count_result = await self.db.execute(count_statement)
        total_records = count_result.scalar_one()

        query = (
            select(Book)
            .where(Book.category.ilike(f"%{category}%"))
            .order_by(Book.title)
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(query)
        books = list(result.scalars().all())

        return books, total_records

    async def get_low_stock(
        self, threshold: int = 10, page: int = 1, limit: int = 10
    ) -> Tuple[list[Book], int]:
        offset = (page - 1) * limit

        count_statement = (
            select(func.count())
            .select_from(Book)
            .where(Book.stock_quantity < threshold)
        )
        count_result = await self.db.execute(count_statement)
        total_records = count_result.scalar_one()

        query = (
            select(Book)
            .where(Book.stock_quantity < threshold)
            .order_by(Book.stock_quantity)
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(query)
        books = list(result.scalars().all())

        return books, total_records

    async def update(self, book: Book) -> Book:
        try:
            await self.db.commit()
            await self.db.refresh(book)
            return book
        except Exception as e:
            await self.db.rollback()
            raise Exception(f"Error al actualizar libro: {e!s}") from e

    async def delete(self, book: Book) -> bool:
        try:
            await self.db.delete(book)
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            raise Exception(f"Error al eliminar libro: {e!s}") from e
