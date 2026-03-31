from app.exceptions import BookNotFoundException
from app.models.api_response import PaginationInfo
from app.models.book import Book
from app.repositories.book_repository import BookRepository


class GetBook:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    async def obtener(self, book_id: int) -> Book:
        book = await self.repository.get_by_id(book_id)

        if book is None:
            raise BookNotFoundException(f"El libro con ID {book_id} no fue encontrado")
        
        return book

    async def listar(self, page: int = 1, limit: int = 10) -> PaginationInfo:
        books, total_records = await self.repository.get_all_paginated(
            page=page, limit=limit
        )
        total_pages = (total_records + limit - 1) // limit if total_records > 0 else 0

        return PaginationInfo(
            page=page,
            limit=limit,
            total_pages=total_pages,
            total_records=total_records,
            info=books,
        )

    async def buscar_por_categoria(
        self, category: str, page: int = 1, limit: int = 10
    ) -> PaginationInfo:
        books, total_records = await self.repository.search_by_category(
            category=category.strip().capitalize(), page=page, limit=limit
        )
        total_pages = (total_records + limit - 1) // limit if total_records > 0 else 0

        return PaginationInfo(
            page=page,
            limit=limit,
            total_pages=total_pages,
            total_records=total_records,
            info=books,
        )

    async def bajo_stock(
        self, threshold: int = 10, page: int = 1, limit: int = 10
    ) -> PaginationInfo:
        books, total_records = await self.repository.get_low_stock(
            threshold=threshold, page=page, limit=limit
        )
        total_pages = (total_records + limit - 1) // limit if total_records > 0 else 0

        return PaginationInfo(
            page=page,
            limit=limit,
            total_pages=total_pages,
            total_records=total_records,
            info=books,
        )

    @staticmethod
    def _to_dict(book: Book) -> dict:
        return {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "cost_usd": book.cost_usd,
            "selling_price_local": book.selling_price_local,
            "stock_quantity": book.stock_quantity,
            "category": book.category,
            "supplier_country": book.supplier_country,
            "created_at": book.created_at,
            "updated_at": book.updated_at,
        }
