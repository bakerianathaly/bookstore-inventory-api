from decimal import Decimal

import pytest
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import SQLModel

from app.models.book import Book
from app.repositories.book_repository import BookRepository


@pytest.fixture
async def db_session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session


@pytest.fixture
def repo(db_session: AsyncSession):
    return BookRepository(db_session)


@pytest.fixture
def sample_book():
    return Book(
        title="Test Book",
        author="Test Author",
        isbn="1234567890",
        cost_usd=Decimal("10.00"),
        stock_quantity=15,
        category="Fiction",
        supplier_country="US",
    )


class TestBookRepository:
    @pytest.mark.asyncio
    async def test_create_book(self, repo: BookRepository, sample_book: Book):
        result = await repo.create(sample_book)
        assert result.id is not None
        assert result.title == "Test Book"

    @pytest.mark.asyncio
    async def test_get_by_id(self, repo: BookRepository, sample_book: Book):
        created = await repo.create(sample_book)
        found = await repo.get_by_id(created.id)
        assert found is not None
        assert found.id == created.id

    @pytest.mark.asyncio
    async def test_get_by_isbn(self, repo: BookRepository, sample_book: Book):
        created = await repo.create(sample_book)
        found = await repo.get_by_isbn("1234567890")
        assert found is not None
        assert found.id == created.id

    @pytest.mark.asyncio
    async def test_get_all_paginated(self, repo: BookRepository):
        for i in range(15):
            book = Book(
                title=f"Book {i}",
                author="Author",
                isbn=f"12345678{i:02d}",
                cost_usd=Decimal("10.00"),
                stock_quantity=10,
                category="Test",
                supplier_country="US",
            )
            await repo.create(book)

        books, total = await repo.get_all_paginated(page=1, limit=10)
        assert total == 15
        assert len(books) == 10

    @pytest.mark.asyncio
    async def test_search_by_category(self, repo: BookRepository, sample_book: Book):
        await repo.create(sample_book)
        book2 = Book(
            title="Another Book",
            author="Author 2",
            isbn="9876543210",
            cost_usd=Decimal("8.00"),
            stock_quantity=5,
            category="Science",
            supplier_country="UK",
        )
        await repo.create(book2)

        books, total = await repo.search_by_category("Fiction")
        assert total == 1

    @pytest.mark.asyncio
    async def test_get_low_stock(self, repo: BookRepository):
        book1 = Book(
            title="Low Stock",
            author="Author",
            isbn="1111111111",
            cost_usd=Decimal("5.00"),
            stock_quantity=3,
            category="Test",
            supplier_country="US",
        )
        book2 = Book(
            title="High Stock",
            author="Author",
            isbn="2222222222",
            cost_usd=Decimal("5.00"),
            stock_quantity=100,
            category="Test",
            supplier_country="US",
        )
        await repo.create(book1)
        await repo.create(book2)

        books, total = await repo.get_low_stock(threshold=10)
        assert total == 1
        assert books[0].title == "Low Stock"

    @pytest.mark.asyncio
    async def test_delete_book(self, repo: BookRepository, sample_book: Book):
        created = await repo.create(sample_book)
        result = await repo.delete(created)
        assert result is True

        found = await repo.get_by_id(created.id)
        assert found is None
