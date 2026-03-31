import pytest
from sqlmodel import Session, SQLModel, create_engine

from app.models.permissions import ProductoCreate
from app.repositories.permissions_repository import PermissionsRepository
from app.services.permissions import PermissionsUseCase


@pytest.fixture(name="db_session")
def db_session_fixture():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="repo")
def repo_fixture(db_session: Session):
    return PermissionsRepository(db_session)


@pytest.fixture(name="service")
def service_fixture(repo: PermissionsRepository):
    return PermissionsUseCase(repo)


@pytest.fixture(name="producto_data")
def producto_data_fixture():
    return ProductoCreate(
        nombre="Producto Test",
        descripcion="Descripción de prueba",
        precio=100.50,
        stock=10,
    )
