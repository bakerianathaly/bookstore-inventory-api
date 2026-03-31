from decimal import Decimal

import pytest
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.models.book import BookCreate
from app.repositories.book_repository import BookRepository
from app.services.book import BookUseCase


@pytest.fixture
async def db_session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    from sqlmodel import SQLModel

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session


@pytest.fixture
def repo(db_session: AsyncSession):
    return BookRepository(db_session)


@pytest.fixture
def service(repo: BookRepository):
    return BookUseCase(repo)


@pytest.fixture
def book_data():
    return BookCreate(
        title="El Quijote",
        author="Miguel de Cervantes",
        isbn="9788437604947",
        cost_usd=Decimal("15.99"),
        stock_quantity=25,
        category="Literatura Clásica",
        supplier_country="ES",
    )


@pytest.fixture
def book_data_2():
    return BookCreate(
        title="Cien Años de Soledad",
        author="Gabriel García Márquez",
        isbn="9780307474728",
        cost_usd=Decimal("12.50"),
        stock_quantity=5,
        category="Literatura Clásica",
        supplier_country="CO",
    )
