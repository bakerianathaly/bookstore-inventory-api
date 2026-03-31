# AGENTS.md

Este archivo proporciona guías y comandos para trabajar en este proyecto.

## Visión General del Proyecto

- **Framework**: FastAPI con SQLModel ORM
- **Base de datos**: PostgreSQL
- **Versión de Python**: 3.12
- **Contenedor**: Docker (imagen Python slim)
- **Gestor de dependencias**: uv (basado en Rust)

## Entorno de Desarrollo

### Comandos Docker

```bash
# Construir y ejecutar la aplicación
docker compose -f docker-compose.test.yml up --build

# Detener la aplicación
docker compose -f docker-compose.test.yml down

# Ver logs
docker compose -f docker-compose.test.yml logs -f

# Acceder al shell del contenedor (si es necesario)
docker compose -f docker-compose.test.yml run --rm web-test /bin/sh
```

### Comandos Locales de Python (uv)

```bash
# Crear entorno virtual e instalar dependencias
uv sync

# Ejecutar la aplicación localmente
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8020

# Agregar una dependencia (ejecuta uv lock automáticamente)
uv add <paquete>

# Remover una dependencia (ejecuta uv lock automáticamente)
uv remove <paquete>

# Bloquear dependencias (SOLO si editaste pyproject.toml manualmente)
uv lock
```

### Gestión de Dependencias

#### Agregar una nueva librería (recomendado)

```bash
# 1. Agregar la librería (uv actualiza pyproject.toml + ejecuta uv lock automáticamente)
uv add requests

# 2. Subir cambios
git add .
git commit -m "add requests dependency"

# 3. Reconstruir Docker (instala la nueva librería)
docker compose -f docker-compose.test.yml up --build
```

#### Remover una librería

```bash
# 1. Remover la librería (uv actualiza pyproject.toml + ejecuta uv lock automáticamente)
uv remove requests

# 2. Subir cambios
git add .
git commit -m "remove requests dependency"

# 3. Reconstruir Docker
docker compose -f docker-compose.test.yml up --build
```

#### Cuándo ejecutar `uv lock` manualmente

| Situación | ¿Necesita `uv lock`? |
|-----------|----------------------|
| `uv add paquete` | No (automático) |
| `uv remove paquete` | No (automático) |
| Editar `pyproject.toml` manualmente | Sí (obligatorio) |
| Desplegar a producción | No (lock file en repo) |
| Cambió solo código Python | No |

#### Dónde ejecutar los comandos

| Comando | Dónde ejecutar |
|---------|----------------|
| `uv add / uv remove` | Local (tu máquina) |
| `uv lock` | Local (tu máquina) |
| `docker compose up --build` | Local (construye el contenedor) |
| Tu código corriendo | Dentro del contenedor |

**Regla:** Docker **lee** el lock file, no lo modifica. Sempre regenera `uv.lock` en local antes de construir.

### Dependencias requeridas para Async

Para usar operaciones asíncronas con PostgreSQL, se necesita el driver `asyncpg`:

```bash
uv add asyncpg
```

Este driver es requerido para la configuración async de SQLModel/SQLAlchemy.

## Linting y Formato

Este proyecto usa **Ruff** para linting y orden de imports, y **Black** para formateo de código.

### Comandos

```bash
# Ejecutar Ruff linter en todo el proyecto
uv run ruff check .

# Ejecutar Ruff con auto-fix
uv run ruff check . --fix

# Eliminar imports no utilizados automáticamente
uv run ruff check . --fix --select F401

# Formatear código con Black
uv run ruff format .

# Verificar si el código está bien formateado
uv run ruff format --check .

# Ejecutar ambos (recomendado antes de hacer commit)
uv run ruff check . --fix && uv run ruff format .

# Ejecutar todo (eliminar imports + formatear)
uv run ruff check . --fix --select F401 && uv run ruff format .
```

### Configuración (pyproject.toml)

```toml
[tool.ruff]
select = ["F401"]  # F401 = imports no utilizados

[tool.ruff.lint]
fixable = ["F401"]  # Permite auto-fix de F401
```

- **Longitud de línea**: 88 caracteres (default de Black)
- **Python objetivo**: 3.12

## Tests

Este proyecto usa **pytest** para tests unitarios e integración.

### Dependencias de test (pyproject.toml)

```toml
[dependency-groups]
dev = [
    "ruff>=0.15.7",
    "pytest>=8.0.0",
    "pytest-cov>=5.0.0",
    "httpx>=0.27.0",
]
```

### Estructura de tests

```
tests/
├── __init__.py
├── conftest.py              # Fixtures compartidas (db_session, repo, service)
├── services/
│   ├── __init__.py
│   ├── test_crear_producto.py
│   ├── test_leer_producto.py
│   └── test_eliminar_producto.py
└── repositories/
    ├── __init__.py
    └── test_producto_repository.py
```

### Ejecutar Tests (vía uv - local)

```bash
# Ejecutar todos los tests
uv run pytest

# Ejecutar con salida verbose
uv run pytest -v

# Ejecutar tests en un archivo específico
uv run pytest tests/services/test_crear_producto.py

# Ejecutar una función de test específica
uv run pytest tests/services/test_crear_producto.py::TestCrearProducto::test_crear_producto_exitoso

# Ejecutar tests que coincidan con un patrón
uv run pytest -k "test_crear"

# Ejecutar con reporte de cobertura
uv run pytest --cov=app --cov-report=term-missing
```

### Ejecutar Tests (vía Docker)

```bash
# Construir y ejecutar tests
docker compose -f docker-compose.test.yml run --rm web-test uv run pytest -v

# Ejecutar tests con cobertura
docker compose -f docker-compose.test.yml run --rm web-test uv run pytest --cov=app --cov-report=term-missing

# Ejecutar tests en un archivo específico
docker compose -f docker-compose.test.yml run --rm web-test uv run pytest tests/services/test_crear_producto.py -v
```

### Fixtures compartidas (conftest.py)

```python
import pytest
from sqlmodel import Session, SQLModel, create_engine

from app.models.producto import ProductoCreate
from app.repositories.producto_repository import PermissionsRepository
from app.services.producto import PermissionsUseCase


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
```

### Convenciones de Tests

- Colocar tests en directorio `tests/` en la raíz del proyecto
- Nombres de archivos: `test_<nombre_modulo>.py`
- Nombres de funciones: `test_<descripción>`
- Nombres de clases: `Test<NombreClase>`
- Usar fixtures de pytest para setup compartido
- Usar SQLite en memoria para tests de repositorio
- Usar `pytest.raises` para capturar excepciones esperadas

### Ejemplo de test

```python
from decimal import Decimal
import pytest

from app.models.producto import ProductoCreate
from app.services.producto import PermissionsUseCase


class TestCrearProducto:
    def test_crear_producto_exitoso(
        self,
        service: PermissionsUseCase,
        producto_data: ProductoCreate,
    ):
        producto = service.crear.execute(producto_data)

        assert producto.nombre == producto_data.nombre
        assert producto.id is not None

    def test_crear_producto_precio_negativo(self, service: PermissionsUseCase):
        data = ProductoCreate(
            nombre="Producto Test",
            precio=Decimal("-5.00"),
            stock=10,
        )

        with pytest.raises(ValueError) as exc:
            service.crear.execute(data)

        assert "precio" in str(exc.value).lower()
```

## Guías de Estilo de Código

### Estilo General

- Seguir las guías de estilo **PEP 8**
- Usar **type hints** para todas las firmas de funciones y atributos de clase
- Usar **f-strings** para formateo de strings
- Longitud máxima de línea: 88 caracteres

### Imports

Organizar imports en el siguiente orden (usar `ruff check . --fix` para auto-ordenar):

1. Imports de la librería estándar
2. Imports de terceros
3. Imports locales de la aplicación

Usar **imports absolutos** desde la raíz del proyecto:

```python
# Correcto
from app.db.sessions import engine
from fastapi import FastAPI

# Incorrecto
from .db.session import engine
```

### Convenciones de Nombres

| Elemento | Convención | Ejemplo |
|----------|------------|---------|
| Variables | snake_case | `user_name`, `total_count` |
| Funciones | snake_case | `get_user_by_id`, `calculate_total` |
| Clases | PascalCase | `UserModel`, `OrderService` |
| Constantes | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT` |
| Miembros privados | Guion bajo al inicio | `_internal_state`, `_private_method` |

### Type Hints

Siempre incluir type hints para parámetros de funciones y valores de retorno:

```python
# Correcto
def process_user(user_id: int, name: str) -> dict[str, Any]:
    return {"id": user_id, "name": name}

# Incorrecto
def process_user(user_id, name):
    return {"id": user_id, "name": name}
```

### Docstrings

Usar docstrings estilo Google:

```python
def calculate_total(items: list[float], tax_rate: float) -> float:
    """Calcula el precio total incluyendo impuesto.

    Args:
        items: Lista de precios de artículos.
        tax_rate: Tasa de impuesto como decimal (ej: 0.1 para 10%).

    Returns:
        Precio total incluyendo impuesto.

    Raises:
        ValueError: Si la lista de items está vacía o tax_rate es negativo.
    """
    if not items:
        raise ValueError("La lista de items no puede estar vacía")
    if tax_rate < 0:
        raise ValueError("La tasa de impuesto no puede ser negativa")
    return sum(items) * (1 + tax_rate)
```

### Manejo de Errores

- Usar `HTTPException` para errores a nivel de API con códigos de estado apropiados
- Siempre usar `try/finally` para limpieza de recursos (ej: sesiones de base de datos)
- Crear excepciones personalizadas para errores específicos del dominio
- Usar rollback en operaciones asíncronas para manejar errores de BD

**Códigos HTTP recomendados:**

| Código | Cuándo usarlo |
|--------|---------------|
| `200` | Operación exitosa (GET) |
| `201` | Creación exitosa (POST) |
| `400` | Error de validación datos |
| `401` | Error de base de datos / No autorizado |
| `404` | Recurso no encontrado |
| `422` | Error de validación de schema (Pydantic) |
| `500` | Error interno del servidor |

**Ejemplo con excepciones personalizadas:**

```python
# app/exceptions.py
class DatabaseException(Exception):
    """Error genérico de base de datos"""
    pass


class ValidationException(Exception):
    """Error de validación de datos"""
    pass
```

**En el repository (con rollback):**

```python
async def create(self, new_permission: Permissions) -> Permissions:
    try:
        self.db.add(new_permission)
        await self.db.commit()
        await self.db.refresh(new_permission)
        return new_permission
    except Exception as e:
        await self.db.rollback()
        raise DatabaseException(f"Error al crear permiso: {str(e)}") from e
```

**En el endpoint:**

```python
from fastapi import HTTPException, status

@router.post("/", response_model=APIResponse[Permissions])
async def crear_recurso(
    response: Response,
    data: SchemaCreate,
    service: Service = Depends(get_service),
) -> APIResponse[Permissions]:
    try:
        outcome = await service.create.execute(data)
        return APIResponse(success=True, message="Creado", outcome=[outcome])
    except ValidationException as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return APIResponse(success=False, message=str(e), errors=[str(e)])
    except DatabaseException as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return APIResponse(success=False, message="Error de base de datos", errors=[str(e)])
```

## Patrones de FastAPI

### Inyección de Dependencias

Usar la inyección de dependencias de FastAPI para sesiones de base de datos:

```python
from fastapi import Depends
from sqlmodel import Session

def get_db():
    with Session(engine) as session:
        yield session

@app.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### Prefijo de URL global (api/v1)

Para agregar un prefijo común a todas las rutas (ej: `/api/v1/`), se configura en `app/main.py` al incluir los routers:

```python
app.include_router(health_router, prefix="/api/v1")
app.include_router(permissions_router, prefix="/api/v1")
```

Esto genera URLs como:
- `/api/v1/productos`
- `/api/v1/health`

**Si necesitás un prefijo diferente para un router específico:** Lo configurás directamente en el propio router:

```python
# En app/api/productos.py
router = APIRouter(prefix="/productos", tags=["productos"])
```

**Nota:** El prefijo del router es relativo al prefijo global. Si tenés `prefix="/api/v1"` en `include_router` y `prefix="/productos"` en el router, la URL final será `/api/v1/productos`.

### Registro de Dependencias (deps.py)

**Ubicación:** `app/deps.py` (no en `app/api/` porque esa carpeta es solo para endpoints)

Declaraciones centralizadas de dependencias:

```python
from fastapi import Depends
from sqlmodel import Session

from app.db.sessions import get_db
from app.repositories.producto_repository import PermissionsRepository
from app.services.producto import PermissionsUseCase


class PermissionsDeps:
    @staticmethod
    def get_repository(db: Session = Depends(get_db)) -> PermissionsRepository:
        return PermissionsRepository(db)

    @staticmethod
    def get_service(
        repo: PermissionsRepository = Depends(get_repository),
    ) -> PermissionsUseCase:
        return PermissionsUseCase(repo)
```

Uso en endpoints:

```python
from app.deps import PermissionsDeps

@router.get("/productos")
def listar(
    service: PermissionsUseCase = Depends(PermissionsDeps.get_service),
):
    return service.leer.listar()

# O inyectar solo el repositorio
@router.get("/tiendas")
def listar_tiendas(
    repo: PermissionsRepository = Depends(PermissionsDeps.get_repository),
):
    return repo.get_all()
```

### Patrón Service Layer (Facade + Casos de Uso)

Los servicios están separados por operación CRUD con una fachada:

```
app/services/producto/
├── __init__.py              # Exporta PermissionsUseCase
├── producto_service.py      # Fachada
├── crear_producto.py        # C: crear_producto(), crear_masivo()
├── leer_producto.py         # R: listar(), obtener()
├── actualizar_producto.py   # U: actualizar()
└── eliminar_producto.py     # D: eliminar()
```

Fachada:

```python
class PermissionsUseCase:
    def __init__(self, repository: PermissionsRepository):
        self.crear = CrearProducto(repository)
        self.leer = LeerProducto(repository)
        self.actualizar = ActualizarProducto(repository)
        self.eliminar = EliminarProducto(repository)
```

Caso de Uso:

```python
class CrearProducto:
    def __init__(self, repository: PermissionsRepository):
        self.repository = repository

    def execute(self, data: ProductoCreate) -> Producto:
        self._validar(data)
        return self.repository.create(data)

    def _validar(self, data: ProductoCreate) -> None:
        if data.precio < Decimal("0.01"):
            raise ValueError("El precio debe ser mayor o igual a 0.01")
```

Uso en endpoint:

```python
@router.post("/productos")
def crear_producto(
    data: ProductoCreate,
    service: PermissionsUseCase = Depends(PermissionsDeps.get_service),
):
    return service.crear.execute(data)
```

### Patrones Async

Este proyecto usa operaciones asíncronas con SQLModel/SQLAlchemy + asyncpg.

**Estructura recomendada:**

```python
# En endpoints: usar async def
from fastapi import APIRouter

router = APIRouter()

@router.get("/items/{item_id}")
async def get_item(item_id: int) -> Item:
    item = await service.leer.obtener(item_id)
    return item

# En repository: usar AsyncSession y await
from sqlalchemy.ext.asyncio import AsyncSession

class PermissionsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, permission_id: UUID) -> Permissions:
        statement = select(Permissions).where(Permissions.id == permission_id)
        result = await self.db.exec(statement)
        return result.one_or_none()

# En deps: configurar async_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

async_engine = create_async_engine(
    str(engine.url).replace("postgresql://", "postgresql+asyncpg://"),
    pool_pre_ping=True,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(async_engine) as session:
        yield session
```

### Modelo de Respuesta Estándar (APIResponse)

Todos los endpoints deben responder con el mismo formato usando `APIResponse`.

**Ubicación:** `app/models/api_response.py`

**Modelo:**

```python
from typing import Any, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool = Field(default=True, description="Indicador de éxito")
    message: str = Field(default="", description="Mensaje descriptivo")
    outcome: list[Any] = Field(default_factory=list, description="Datos de respuesta")
    errors: list[str] = Field(default_factory=list, description="Lista de errores")
```

**Uso en endpoints:**

```python
from uuid import UUID
from fastapi import APIRouter, status

from app.models.api_response import APIResponse
from app.models.permissions import Permissions, PermissionsCreate

router = APIRouter(prefix="/permissions", tags=["Permisos"])

# POST - Crear
@router.post("/", response_model=APIResponse[Permissions])
def crear_permiso(permiso: PermissionsCreate):
    nuevo = service.crear.execute(permiso)
    return APIResponse(
        success=True,
        message="Permiso creado",
        outcome=[nuevo]  #Siempre debe ser lista
    )

# GET - Listar
@router.get("/", response_model=APIResponse[list[Permissions]])
def listar_permisos():
    permisos = service.leer.listar()
    return APIResponse(
        success=True,
        message="Lista de permisos",
        outcome=permisos
    )

# GET - Obtener uno
@router.get("/{permiso_id}", response_model=APIResponse[Permissions])
def obtener_permiso(permiso_id: UUID):
    permiso = service.leer.obtener(permiso_id)
    if not permiso:
        return APIResponse(
            success=False,
            message="Permiso no encontrado",
            errors=["Permiso no encontrado"]
        )
    return APIResponse(
        success=True,
        message="Permiso obtenido",
        outcome=[permiso]  #Siempre debe ser lista
    )

# DELETE - Eliminar
@router.delete("/{permiso_id}", response_model=APIResponse[None])
def eliminar_permiso(permiso_id: UUID):
    resultado = service.eliminar.execute(permiso_id)
    if not resultado:
        return APIResponse(
            success=False,
            message="Permiso no encontrado",
            errors=["Permiso no encontrado"]
        )
    return APIResponse(
        success=True,
        message="Permiso eliminado",
        outcome=[]  # Lista vacía para delete
    )
```

**Ejemplo de respuesta exitosa:**

```json
{
  "success": true,
  "message": "Permiso creado",
  "outcome": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "permission_code": "permissions_create",
      "functionality": "permissions",
      "descripcion": "Crear permisos",
      "type": "endpoint",
      "is_active": true
    }
  ],
  "errors": []
}
```

**Ejemplo de respuesta con error:**

```json
{
  "success": false,
  "message": "Permiso no encontrado",
  "outcome": [],
  "errors": ["Permiso no encontrado"]
}
```

**Nota importante:**
- `outcome` siempre debe ser una lista, aunque sea un solo elemento
- Usar `APIResponse[None]` para operaciones que no retornan datos (DELETE)
- El campo `code` (código HTTP) se omite porque FastAPI lo maneja automáticamente

## Estructura de Archivos

```
cronicos/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Punto de entrada FastAPI
│   ├── deps.py                    # Declaraciones centralizadas de dependencias
│   ├── exceptions.py              # Excepciones personalizadas del dominio
│   ├── api/
│   │   ├── __init__.py
│   │   ├── health.py              # Endpoint de health check
│   │   └── permissions.py         # Endpoints de permisos
│   ├── db/
│   │   └── sessions.py            # Configuración de sesión SQLModel
│   ├── models/
│   │   ├── __init__.py
│   │   ├── api_response.py        # Modelo de respuesta estándar
│   │   ├── permissions.py         # Modelo de permisos
│   │   └── roles.py               # Modelo de roles
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── permissions_repository.py # Capa de acceso a datos
│   └── services/
│       └── permissions/
│           ├── __init__.py
│           ├── producto_service.py #Fachada (PermissionsUseCase)
│           ├── create.py            # Caso de uso: crear
│           ├── leer_producto.py     # Caso de uso: leer
│           ├── actualizar_producto.py # Caso de uso: actualizar
│           └── eliminar_producto.py # Caso de uso: eliminar
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── test_crear_producto.py
│   │   ├── test_leer_producto.py
│   │   └── test_eliminar_producto.py
│   └── repositories/
│       ├── __init__.py
│       └── test_producto_repository.py
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── Docker/
│   ├── local/
│   │   └── Dockerfile
│   ├── test/
│   │   ├── Dockerfile
│   │   ├── entrypoint.sh
│   │   └── start.sh
│   └── prod/
│       ├── Dockerfile
│       ├── entrypoint.sh
│       └── start.sh
├── pyproject.toml
├── uv.lock
├── alembic.ini
├── docker-compose.local.yml
├── docker-compose.test.yml
├── docker-compose.prod.yml
├── .env
├── .gitignore
├── AGENTS.md
└── README.md
```

## Variables de Entorno

Variables de entorno requeridas (ver archivo `.env`):

- `DATABASE_URL`: Cadena de conexión PostgreSQL (ej: `postgresql://user:pass@host:5432/dbname`)

## SQLModel

Este proyecto usa **SQLModel** que combina SQLAlchemy ORM + Schemas Pydantic en una sola librería.

### Crear un nuevo modelo (tabla)

Crear un archivo en `app/models/` con el modelo y sus schemas de API:

```python
# app/models/tienda.py
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlmodel import Field, SQLModel


# ─── Modelo DB ───────────────────────────────────────────────
class Tienda(SQLModel, table=True):
    __tablename__ = "tiendas"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(UUID, primary_key=True),
    )
    nombre: str = Field(max_length=255)
    direccion: Optional[str] = None
    telefono: Optional[str] = Field(default=None, max_length=20)
    activa: bool = Field(default=True)
    created_at: datetime = Field(
        default=None,
        sa_column_kwargs={"server_default": func.now()},
    )


# ─── Schemas API ─────────────────────────────────────────────
class TiendaCreate(SQLModel):
    nombre: str = Field(max_length=255)  # Se puede usar min_length=1
    direccion: Optional[str] = None
    telefono: Optional[str] = None


class TiendaResponse(SQLModel):
    id: uuid.UUID
    nombre: str
    direccion: Optional[str]
    telefono: Optional[str]
    activa: bool
    created_at: datetime
```

Luego exportar desde `app/models/__init__.py`:

```python
from app.models.producto import Producto, ProductoCreate, ProductoResponse
from app.models.tienda import Tienda, TiendaCreate, TiendaResponse

__all__ = [
    "Producto", "ProductoCreate", "ProductoResponse",
    "Tienda", "TiendaCreate", "TiendaResponse",
]
```

### Referencia de tipos de campos

```python
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID

class Example(SQLModel, table=True):
    # String con longitud máxima
    nombre: str = Field(max_length=255)

    # String requerido y único
    codigo: str = Field(max_length=50, unique=True, nullable=False)

    # Text (longitud ilimitada) - usar sa_column para tipo Text
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))

    # Entero con default
    stock: int = Field(default=0)

    # Decimal (Numeric)
    precio: Decimal = Field(max_digits=10, decimal_places=2)

    # Booleano
    activo: bool = Field(default=True)

    # Campo opcional
    telefono: Optional[str] = Field(default=None, max_length=20)

    # UUID como llave primaria
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(UUID, primary_key=True),
    )
```

### Cuándo usar `sa_column`

En SQLModel, `sa_column` se usa **solo cuando necesitas un tipo de columna específico que Field no soporta nativamente**.

**Casos donde NO necesitas `sa_column`:**

SQLModel mapea tipos Python automáticamente:

```python
# SQLModel sabe cómo manejar estos tipos
nombre: str = Field(max_length=255)        # VARCHAR(255)
stock: int = Field(default=0)              # INTEGER
precio: Decimal = Field(decimal_places=2)  # NUMERIC
activo: bool = Field(default=True)         # BOOLEAN
```

**Casos donde SÍ necesitas `sa_column`:**

Cuando el tipo no tiene equivalente directo en Python:

```python
from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID

# Text (longitud ilimitada) - Python no tiene "Text", solo "str"
descripcion: str = Field(default=None, sa_column=Column(Text))

# UUID como primary key - Python tiene uuid.UUID pero no mapea directo a PostgreSQL UUID
id: uuid.UUID = Field(
    default_factory=uuid.uuid4,
    sa_column=Column(UUID, primary_key=True),
)

# JSONB (PostgreSQL)
metadata: dict = Field(default=None, sa_column=Column(JSONB))
```

**Resumen:**

| Situación | Usar `sa_column` |
|-----------|------------------|
| `str`, `int`, `bool`, `Decimal` | No |
| `Text` (longitud ilimitada) | Sí (`Column(Text)`) |
| `UUID` como primary key | Sí (`Column(UUID)`) |
| `JSONB`, `ARRAY`, tipos PostgreSQL | Sí |
| `server_default` (ej: `func.now()`) | Sí (`sa_column_kwargs={"server_default": func.now()}`) |

**Regla:** Si `Field()` normal funciona, úsalo. Solo recurre a `sa_column` cuando necesites un tipo SQLAlchemy específico.

### Validación de schemas vs Service

En este proyecto, la validación de reglas de negocio se hace en el **service**, no en el schema. El schema solo define la estructura del dato.

**Schema (solo estructura):**
```python
class ProductoCreate(SQLModel):
    nombre: str = Field(max_length=255)  # Se puede usar min_length=1
    descripcion: Optional[str] = None
    precio: Decimal = Field(decimal_places=2)  # Se puede usar gt=0
    stock: int = Field(default=0)  # Se puede usar ge=0
```

**Service (reglas de negocio):**
```python
class CrearProducto:
    MIN_STOCK = 0
    MAX_STOCK = 10000
    MIN_PRECIO = Decimal("0.01")

    def _validar(self, producto_data: ProductoCreate) -> None:
        if producto_data.precio < self.MIN_PRECIO:
            raise ValueError(f"El precio debe ser mayor o igual a {self.MIN_PRECIO}")
        if producto_data.stock < self.MIN_STOCK:
            raise ValueError("El stock no puede ser negativo")
        if producto_data.stock > self.MAX_STOCK:
            raise ValueError(f"El stock no puede exceder {self.MAX_STOCK}")
        if producto_data.nombre and len(producto_data.nombre.strip()) < 3:
            raise ValueError("El nombre debe tener al menos 3 caracteres")
```

**¿Por qué?** Si Pydantic valida en el schema, la excepción ocurre antes de llegar al service, y el service nunca ejecuta su lógica de validación.

**Regla:** El schema define **qué datos entran**, el service define **qué reglas se aplican**.

### Validación de Campos con Enums

Para campos con valores limitados (como tipo de permiso), usar `Enum` de Python para validación automática en el schema.

```python
from enum import Enum


class PermissionType(str, Enum):
    ENDPOINT = "endpoint"
    FRONT = "front"
    NAVIGATION = "navigation"


class PermissionsCreate(SQLModel):
    permission_code: str = Field(max_length=255)
    functionality: str = Field(max_length=255)
    descripcion: str = Field(sa_column=Column(Text))
    type: PermissionType = Field(default=PermissionType.ENDPOINT)
```

**Uso en el service:**

```python
permission_info = Permissions(
    type=permission_data.type.value,  # Convertir Enum a string
    ...
)
```

**边界:** Si el usuario envía un valor inválido, FastAPI automáticamente retorna **422 Unprocessable Entity** con el error de validación.

## Migraciones con Alembic

Alembic funciona igual que con SQLModel puro. La diferencia clave es usar `SQLModel.metadata` en vez de `Base.metadata`.

### Comandos

```bash
# Generar nueva migración (autogenerate)
uv run alembic revision --autogenerate -m "descripción del cambio"

# Aplicar migraciones pendientes
uv run alembic upgrade head

# Ver estado actual de migración
uv run alembic current

# Rollback una migración
uv run alembic downgrade -1

# Ver historial de migraciones
uv run alembic history
```

### Ejemplo: Nueva tabla

```bash
# 1. Crear el modelo en app/models/tienda.py
# 2. Generar migración
uv run alembic revision --autogenerate -m "add tienda table"

# 3. Revisar el archivo generado en alembic/versions/
# 4. Aplicar migración
uv run alembic upgrade head
```

### Ejemplo: Agregar nuevos campos

```bash
# 1. Agregar campos al modelo en app/models/producto.py
# 2. Generar migración
uv run alembic revision --autogenerate -m "add categoria and codigo fields"

# 3. Aplicar migración
uv run alembic upgrade head
```

### Renombrar un campo

Alembic autogenerate **no detecta renames** (ve drop + add). Editar la migración manualmente:

```python
def upgrade() -> None:
    op.alter_column('products', 'nombre', new_column_name='nombre_producto')


def downgrade() -> None:
    op.alter_column('products', 'nombre_producto', new_column_name='nombre')
```

### Cambiar tipo de dato de un campo

Alembic autogenerate detecta cambios de tipo automáticamente:

```python
def upgrade() -> None:
    op.alter_column('products', 'stock',
        existing_type=sa.INTEGER(),
        type_=sa.Numeric(precision=10, scale=2),
        existing_nullable=True
    )


def downgrade() -> None:
    op.alter_column('products', 'stock',
        existing_type=sa.Numeric(precision=10, scale=2),
        type_=sa.INTEGER(),
        existing_nullable=True
    )
```

### Resumen de detección de migraciones

| Operación | Detectado automáticamente | Edición manual necesaria |
|-----------|---------------------------|--------------------------|
| Nueva tabla | ✅ Sí | No |
| Nuevo campo | ✅ Sí | No |
| Eliminar campo | ✅ Sí | No |
| Cambiar tipo de dato | ✅ Sí | No |
| Renombrar campo | ❌ No | Sí, usar `op.alter_column` con `new_column_name` |

### Configuración de alembic/env.py

```python
from app.db.sessions import SQLModel
import app.models

target_metadata = SQLModel.metadata
```

### Migraciones en Producción (vía Docker)

Para aplicar migraciones en el ambiente de producción:

```bash
# 1. Generar migración en local (NO en producción)
uv run alembic revision --autogenerate -m "descripción del cambio"

# 2. Revisar el archivo generado en alembic/versions/
# 3. Commit y push al repo
git add alembic/versions/
git commit -m "add migration: descripción del cambio"
git push

# 4. En producción, aplicar migración antes de levantar el servicio
docker compose -f docker-compose.prod.yml run --rm server uv run alembic upgrade head

# 5. Levantar el servicio
docker compose -f docker-compose.prod.yml up -d
```

**Precauciones:**
- Siempre generar migraciones en local, nunca en producción
- Revisar el archivo generado antes de aplicarlo
- Hacer backup de la base de datos antes de aplicar migraciones en producción
- Aplicar migraciones antes de levantar el servicio nuevo

## Consultas entre Schemas en PostgreSQL

Si tu usuario de BD tiene acceso a múltiples schemas, puedes hacer consultas cruzadas.

### Ejemplo de escenario

```sql
-- SQL puro equivalente
SELECT *
FROM productos.item AS i
INNER JOIN precio.price AS p ON p.item_id = i.id
```

### Opción 1: Modelos con `__table_args__`

Definir cada modelo con su schema:

```python
# app/models/producto.py
class Item(SQLModel, table=True):
    __tablename__ = "item"
    __table_args__ = {"schema": "productos"}

    id: uuid.UUID = Field(
        primary_key=True,
        sa_column=Column(UUID, primary_key=True),
    )
    nombre: str = Field(max_length=255)


# app/models/precio.py
class Price(SQLModel, table=True):
    __tablename__ = "price"
    __table_args__ = {"schema": "precio"}

    id: uuid.UUID = Field(
        primary_key=True,
        sa_column=Column(UUID, primary_key=True),
    )
    item_id: uuid.UUID = Field(
        sa_column=Column(UUID, ForeignKey("productos.item.id"))
    )
    monto: float = Field()
```

**Join con SQLModel:**

```python
from sqlmodel import select, Session
from app.models.producto import Item
from app.models.precio import Price


def obtener_items_con_precios(session: Session):
    statement = (
        select(Item, Price)
        .join(Price, Price.item_id == Item.id)
    )
    results = session.exec(statement).all()
    return results
```

### Opción 2: Query crudo con `text()`

SQL puro directo para máximo control:

```python
from sqlmodel import Session
from sqlalchemy import text as sa_text


# SELECT
def obtener_items_con_precios_crudo(session: Session):
    query = sa_text("""
        SELECT i.id, i.nombre, p.monto
        FROM productos.item AS i
        INNER JOIN precio.price AS p ON p.item_id = i.id
    """)
    results = session.exec(query).all()
    return results


# INSERT
def insertar_precio(session: Session, item_id: str, monto: float):
    query = sa_text("""
        INSERT INTO precio.price (item_id, monto)
        VALUES (:item_id, :monto)
    """)
    session.exec(query, params={"item_id": item_id, "monto": monto})
    session.commit()


# UPDATE
def actualizar_precio(session: Session, item_id: str, monto: float):
    query = sa_text("""
        UPDATE precio.price
        SET monto = :monto
        WHERE item_id = :item_id
    """)
    session.exec(query, params={"item_id": item_id, "monto": monto})
    session.commit()


# DELETE
def eliminar_precio(session: Session, item_id: str):
    query = sa_text("""
        DELETE FROM precio.price
        WHERE item_id = :item_id
    """)
    session.exec(query, params={"item_id": item_id})
    session.commit()
```

### Consideraciones importantes

| Aspecto | Detalle |
|---------|--------|
| Alembic autogenerate | Solo detecta schemas del modelo con `table=True` |
| Permisos BD | El usuario debe tener acceso a ambos schemas |
| Foreign Keys | `ForeignKey("productos.item.id")` referencia con schema completo |
| SQL Injection | Usar siempre `:param` (nunca f-strings para valores) |

### Comparación: Query crudo vs ORM

| Aspecto | Query crudo | ORM |
|---------|-------------|-----|
| Control total | ✅ SQL nativo PostgreSQL | ❌ Limitado a ORM |
| Performance | ✅ Sin overhead de ORM | ❌ Overhead de ORM |
| Flexibilidad | ✅ CTEs, funciones, procedures | ❌ Limitado |
| Sin modelos | ✅ No necesitas definir modelos | ❌ Necesitas modelos |
| Validaciones | ❌ No valida tipos, campos requeridos | ✅ Valida automáticamente |
| Type hints | ❌ No tienes autocompletado | ✅ Autocompletado |
| Mantenibilidad | ❌ Cambios de BD no se reflejan | ✅ Se reflejan automáticamente |
