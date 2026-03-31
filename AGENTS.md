# AGENTS.md

Guía de trabajo para el proyecto **Bookstore Inventory API**.

## Visión General

- **Framework**: FastAPI
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Base de datos**: PostgreSQL 16 (driver: `asyncpg`)
- **Python**: 3.12
- **Gestor de dependencias**: uv
- **Docker**: Imagen Python slim con uv multi-stage build
- **Entorno local**: Docker Compose con PostgreSQL

## Estructura del Proyecto

```
bookstore-inventory-api/
├── app/
│   ├── main.py                     # FastAPI app, incluye router con prefix /api/v1
│   ├── deps.py                     # Inyección de dependencias centralizada
│   ├── exceptions.py               # Excepciones del dominio
│   ├── api/
│   │   ├── __init__.py
│   │   └── books.py                # Endpoints CRUD + calculate-price
│   ├── db/
│   │   └── sessions.py             # AsyncSession + async_engine
│   ├── models/
│   │   ├── __init__.py
│   │   ├── api_response.py         # APIResponse[T], PaginationInfo
│   │   └── book.py                 # Book, BookCreate, BookUpdate, PriceCalculationResponse
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── book_repository.py      # Acceso a datos (async)
│   └── services/
│       ├── __init__.py
│       └── book/
│           ├── __init__.py         # Exporta BookUseCase
│           ├── book_service.py     # Fachada: BookUseCase
│           ├── create_book.py      # Caso de uso: crear
│           ├── get_book.py         # Caso de uso: listar, obtener, buscar
│           ├── update_book.py      # Caso de uso: actualizar
│           ├── delete_book.py      # Caso de uso: eliminar
│           └── calculate_price.py  # Caso de uso: calcular precio con tasa de cambio
├── shared/
│   └── config.py                   # Variables de entorno (starlette.config)
├── tests/
│   ├── conftest.py                 # Fixtures: db_session, repo, service, book_data
│   ├── repositories/
│   │   └── test_book_repository.py
│   └── services/
│       ├── test_create_book.py
│       ├── test_get_book.py
│       ├── test_update_book.py
│       ├── test_delete_book.py
│       └── test_calculate_price.py
├── alembic/
│   ├── env.py
│   └── versions/
├── Docker/local/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── start.sh
├── pyproject.toml
├── uv.lock
├── alembic.ini
├── docker-compose.local.yml
└── .env
```

## Variables de Entorno (.env)

```
MY_CUSTOM_USER=pruebas
MY_CUSTOM_PASS=Pruebas123*
MY_CUSTOM_DB=bookstore-inventory
DATABASE_URL=postgresql://pruebas:Pruebas123*@db:5432/bookstore-inventory
EXCHANGE_RATE_API_URL=https://api.exchangerate-api.com/v4/latest/USD
TARGET_CURRENCY=VES
```

Se acceden vía `shared/config.py` usando `starlette.config.Config`.

## Comandos Docker

```bash
# Levantar app + PostgreSQL
docker compose -f docker-compose.local.yml up --build

# Detener
docker compose -f docker-compose.local.yml down

# Ver logs
docker compose -f docker-compose.local.yml logs -f
```

La app queda en `http://localhost:8020`.

## Comandos Locales (uv)

```bash
# Instalar dependencias
uv sync

# Ejecutar la app
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8020

# Agregar dependencia
uv add <paquete>

# Remover dependencia
uv remove <paquete>

# Bloquear dependencias (solo si editaste pyproject.toml manualmente)
uv lock
```

**Regla:** Docker lee el lock file, no lo modifica. Siempre regenerar `uv.lock` local antes de construir.

## Linting y Formato

```bash
# Lint con auto-fix
uv run ruff check . --fix

# Eliminar imports no usados
uv run ruff check . --fix --select F401

# Formatear código
uv run ruff format .

# Verificar formato
uv run ruff format --check .

# Todo junto (recomendado antes de commit)
uv run ruff check . --fix --select F401 && uv run ruff format .
```

Configuración en `pyproject.toml`:
- Ruff para linting (F401 = imports no usados, auto-fix habilitado)
- Longitud de línea: 88 caracteres
- Python objetivo: 3.12

## Tests

```bash
# Todos los tests
uv run pytest -v

# Archivo específico
uv run pytest tests/services/test_create_book.py -v

# Test específico
uv run pytest tests/services/test_create_book.py::TestCreateBook::test_crear_libro_exitoso -v

# Con cobertura
uv run pytest --cov=app --cov-report=term-missing
```

### Fixtures (conftest.py)

Los tests usan SQLite en memoria con `aiosqlite` y `StaticPool` para aislamiento:

```python
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
def service(repo: BookRepository):
    return BookUseCase(repo)
```

### Convenciones de Tests

- Todos los tests son `async` con `@pytest.mark.asyncio`
- Usar `pytest.raises` para excepciones esperadas
- El repositorio retorna `dict` en queries paginadas (no objetos Book)
- Los mocks de httpx requieren `MagicMock` para métodos síncronos (`.json()`) y `AsyncMock` para asíncronos (`.raise_for_status()`)
- Los patches de httpx deben apuntar al módulo local: `app.services.book.calculate_price.httpx.AsyncClient.get`

## Modelo de Dominio

### Book (tabla `books`)

| Campo | Tipo | Notas |
|-------|------|-------|
| `id` | `int` | PK autoincremental |
| `title` | `str` | max 255 chars |
| `author` | `str` | max 255 chars |
| `isbn` | `str` | max 20 chars, único |
| `cost_usd` | `Decimal` | 10 dígitos, 2 decimales |
| `selling_price_local` | `Decimal` | opcional, calculado |
| `stock_quantity` | `int` | default 0 |
| `category` | `str` | max 255 chars |
| `supplier_country` | `str` | max 5 chars |
| `created_at` | `datetime` | default `datetime.now` |
| `updated_at` | `datetime` | default `datetime.now` |

### Schemas

- **BookCreate**: title, author, isbn, cost_usd, stock_quantity, category, supplier_country
- **BookUpdate**: Todos opcionales (solo campos a modificar)
- **PriceCalculationResponse**: book_id, cost_usd, exchange_rate, cost_local, margin_percentage (40%), selling_price_local, currency, calculation_timestamp

## Patrón de Arquitectura

### Service Layer (Facade + Casos de Uso)

```
app/services/book/
├── book_service.py     # Fachada: BookUseCase
├── create_book.py      # service.create.execute(data=...)
├── get_book.py         # service.get.obtener(id) / listar() / buscar_por_categoria() / bajo_stock()
├── update_book.py      # service.update.execute(book_id, data)
├── delete_book.py      # service.delete.execute(book_id)
└── calculate_price.py  # service.calculate_price.execute(book_id)
```

Uso en endpoint:

```python
@router.post("/", response_model=APIResponse[Book])
async def crear_libro(
    data: BookCreate,
    service: BookUseCase = Depends(BookDeps.get_service),
) -> APIResponse[Book]:
    book = await service.create.execute(data=data)
    return APIResponse(success=True, message="El libro fue creado exitosamente", outcome=[book])
```

**Importante:** `execute()` recibe `data` como keyword-only (`execute(data=...)`, no `execute(data)`).

### Inyección de Dependencias (deps.py)

```python
class BookDeps:
    @staticmethod
    def get_repository(db: AsyncSession = Depends(get_db)) -> BookRepository:
        return BookRepository(db)

    @staticmethod
    def get_service(repo: BookRepository = Depends(get_repository)) -> BookUseCase:
        return BookUseCase(repo)
```

Uso en endpoint:

```python
service: BookUseCase = Depends(BookDeps.get_service)
```

### Async en toda la cadena

Todo es `async/await`:
- Endpoints: `async def`
- Repository: `AsyncSession` + `await self.db.execute()`, `await self.db.commit()`
- Service: `await self.repository.get_by_id()`

### Modelo de Respuesta (APIResponse)

Todos los endpoints retornan `APIResponse[T]`:

```python
class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    outcome: list[Any]    # Siempre lista, aunque sea un solo elemento
    errors: list[str]
```

Para listados paginados se usa `APIResponse[PaginationInfo]`:

```python
class PaginationInfo(BaseModel):
    page: int
    limit: int
    total_pages: int
    total_records: int
    info: list
```

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/` | Health check raíz |
| `POST` | `/api/v1/books/` | Crear libro (201) |
| `GET` | `/api/v1/books/` | Listar paginado |
| `GET` | `/api/v1/books/search` | Buscar por categoría |
| `GET` | `/api/v1/books/low-stock` | Libros con stock bajo |
| `GET` | `/api/v1/books/{book_id}` | Obtener por ID |
| `PUT` | `/api/v1/books/{book_id}` | Actualizar libro |
| `DELETE` | `/api/v1/books/{book_id}` | Eliminar libro |
| `POST` | `/api/v1/books/{book_id}/calculate-price` | Calcular precio con tasa de cambio |

## Excepciones del Dominio

| Excepción | Uso |
|-----------|-----|
| `BookNotFoundException` | Libro no existe (404) |
| `BookAlreadyExistsException` | ISBN o título duplicado (400) |
| `ValidationException` | Datos inválidos (400) |
| `ExchangeRateApiException` | Error al consultar API de tasas de cambio (503) |
| `BookListEmptyException` | Listado vacío (204) |
| `ExchangeRateAPIException` | Alias legacy (mismo uso) |

Las excepciones se capturan en los endpoints y se convierten a `APIResponse` con el código HTTP apropiado. El repository hace `rollback` en caso de error de BD.

## Validaciones de Negocio

Las validaciones están en el **service**, no en el schema (Pydantic solo define la estructura).

### CreateBook
- ISBN debe tener formato válido (10 o 13 dígitos, con o sin guiones)
- ISBN no puede duplicarse
- Título no puede duplicarse
- `cost_usd` debe ser mayor a 0
- `stock_quantity` no puede ser negativo

### UpdateBook
- Mismas validaciones que CreateBook pero solo para campos proporcionados
- Los campos no enviados se ignoran (`model_dump(exclude_unset=True)`)

### CalculatePrice
- Obtiene tasa de cambio de la API externa
- Calcula: `cost_local = cost_usd * exchange_rate`
- Margen: 40% sobre el costo local
- Actualiza `selling_price_local` en el libro
- Lanza `ExchangeRateApiException` si la API falla (no hay fallback automático)

## Códigos HTTP

| Código | Uso |
|--------|-----|
| `200` | Operación exitosa |
| `201` | Libro creado |
| `204` | Listado vacío (sin contenido) |
| `400` | Validación fallida / recurso duplicado |
| `404` | Libro no encontrado |
| `503` | API de tasas de cambio no disponible |

## Alembic (Migraciones)

```bash
# Generar migración
uv run alembic revision --autogenerate -m "descripción"

# Aplicar migraciones
uv run alembic upgrade head

# Rollback
uv run alembic downgrade -1

# Estado actual
uv run alembic current
```

`alembic/env.py` usa `shared/config.py` para obtener `DATABASE_URL` y `SQLModel.metadata` como target metadata.

## Guías de Estilo

- **Type hints** en todas las funciones y atributos
- **Imports absolutos** desde la raíz del proyecto (`from app.models.book import Book`)
- **snake_case** para variables y funciones, **PascalCase** para clases
- **Docstrings** estilo Google solo donde aporten claridad
- **f-strings** para formateo
- No agregar imports no usados (ruff F401)
