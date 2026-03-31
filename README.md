# Bookstore Inventory API

API REST para la gestion de inventario de una cadena de librerias. Permite registrar libros, consultar stock, buscar por categoria, detectar bajo inventario y calcular precios de venta local a partir de una tasa de cambio externa.

Stack: FastAPI + SQLModel + PostgreSQL 16 + asyncpg.

## Requisitos previos

- Docker y Docker Compose instalados
- Python 3.12 (solo si queres correr fuera de Docker)
- uv como gestor de dependencias (solo si corres local)

## Levantar el proyecto con Docker

Este es el metodo recomendado. Docker Compose levanta la API y PostgreSQL en la misma red.

**1. Crear el archivo `.env` en la raiz del proyecto:**

```
MY_CUSTOM_USER=pruebas
MY_CUSTOM_PASS=Pruebas123*
MY_CUSTOM_DB=bookstore-inventory
DATABASE_URL=postgresql://pruebas:Pruebas123*@db:5432/bookstore-inventory
EXCHANGE_RATE_API_URL=https://api.exchangerate-api.com/v4/latest/USD
TARGET_CURRENCY=VES
```

El archivo `.env` debe estar en la raiz del proyecto (al mismo nivel que `docker-compose.local.yml`). Docker Compose lo lee automaticamente y lo monta dentro del contenedor.

**2. Construir y levantar los servicios:**

```bash
docker compose -f docker-compose.local.yml up --build
```

Esto construye la imagen de la app (multi-stage con uv) y levanta un contenedor de PostgreSQL 16. El `entrypoint.sh` espera a que PostgreSQL este listo antes de iniciar uvicorn.

**3. Ejecutar la migracion de base de datos:**

Una vez que los contenedores esten corriendo, ejecutar la migracion para crear la tabla `books`:

```bash
docker compose -f docker-compose.local.yml exec server-bookstore-inventory uv run alembic upgrade head
```

Esto es obligatorio. Sin la migracion, la tabla no existe y cualquier peticion a la API fallara. La migracion crea la tabla `books` con todos sus campos, incluyendo la restriccion de unicidad sobre `isbn`.

**4. Verificar que la API esta funcionando:**

```bash
curl http://localhost:8020/
```

Respuesta esperada:

```json
{"message": "Bookstore Inventory API v1.0.0 funcionando"}
```

**5. Ejecutar los tests:**

```bash
docker compose -f docker-compose.local.yml exec server-bookstore-inventory uv run pytest -v
```

## Acceder a Swagger (documentacion interactiva)

FastAPI genera automaticamente la documentacion OpenAPI :

- Swagger UI: `http://localhost:8020/docs`

Desde Swagger se pueden probar todos los endpoints directamente en el navegador. La documentacion incluye los schemas de entrada y salida, codigos de respuesta y ejemplos.

## Variables de entorno

| Variable | Descripcion | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | Cadena de conexion PostgreSQL | `postgresql://pruebas:Pruebas123*@db:5432/bookstore-inventory` |
| `EXCHANGE_RATE_API_URL` | URL de la API de tasas de cambio | `https://api.exchangerate-api.com/v4/latest/USD` |
| `TARGET_CURRENCY` | Moneda local para conversion | `VES` |
| `MY_CUSTOM_USER` | Usuario de PostgreSQL (solo Docker) | `pruebas` |
| `MY_CUSTOM_PASS` | Password de PostgreSQL (solo Docker) | `Pruebas123*` |
| `MY_CUSTOM_DB` | Nombre de la BD (solo Docker) | `bookstore-inventory` |

Las variables se leen mediante `shared/config.py` usando `starlette.config.Config`. Si no se definen, se usan defaults (SQLite para desarrollo sin PostgreSQL).

## Endpoints

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/api/v1/books/` | Crear un libro |
| `GET` | `/api/v1/books/` | Listar libros (paginado) |
| `GET` | `/api/v1/books/search?category=...` | Buscar por categoria |
| `GET` | `/api/v1/books/low-stock?threshold=10` | Libros con stock bajo |
| `GET` | `/api/v1/books/{book_id}` | Obtener un libro por ID |
| `PUT` | `/api/v1/books/{book_id}` | Actualizar un libro |
| `DELETE` | `/api/v1/books/{book_id}` | Eliminar un libro |
| `POST` | `/api/v1/books/{book_id}/calculate-price` | Calcular precio de venta local |

### Ejemplos de uso

**Crear un libro:**

```bash
curl -X POST http://localhost:8020/api/v1/books/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Cien Años de Soledad",
    "author": "Gabriel Garcia Marquez",
    "isbn": "9780307474728",
    "cost_usd": 12.50,
    "stock_quantity": 25,
    "category": "Literatura",
    "supplier_country": "CO"
  }'
```

**Calcular precio de venta:**

```bash
curl -X POST http://localhost:8020/api/v1/books/1/calculate-price
```

Esto consulta la API externa de tasas de cambio, calcula el costo en moneda local (USD * tasa), aplica un margen del 40% y actualiza el `selling_price_local` del libro. Si la API externa falla, retorna 503.

### Respuesta estandar

Todos los endpoints retornan el mismo formato:

```json
{
  "success": true,
  "message": "Libro creado exitosamente",
  "outcome": [ { ... } ],
  "errors": []
}
```

`outcome` siempre es una lista, incluso cuando retorna un solo elemento. Para listados paginados, `outcome` contiene un objeto con `page`, `limit`, `total_pages`, `total_records` y `info` (la lista de resultados).

### Codigos de respuesta

| Codigo | Significado |
|--------|-------------|
| 200 | Operacion exitosa |
| 201 | Libro creado |
| 204 | Listado vacio |
| 400 | Validacion fallida o recurso duplicado |
| 404 | Libro no encontrado |
| 503 | API de tasas de cambio no disponible |

## Arquitectura

El proyecto sigue un patron de Service Layer con separacion por casos de uso. La idea es que cada operacion de negocio este aislada en su propia clase, y una fachada (`BookUseCase`) las agrupe.

```
request -> endpoint -> service (fachada) -> caso de uso -> repository -> DB
```

**Por que esta separacion?** Lo mas comun al ser un proyecto pequeño era tener todo en un service unico con todos los metodos, pero al tener logica de validacion en create y update (ISBN, duplicados, precios) y la llamada HTTP externa en calculate-price, tener cada operacion en un archivo separado hace mas facil testear y mantener. Cada clase tiene una sola responsabilidad.

```
app/services/book/
├── book_service.py     # Fachada: BookUseCase
├── create_book.py      # Valida y crea
├── get_book.py         # Consultas (obtener, listar, buscar, bajo stock)
├── update_book.py      # Valida y actualiza (solo campos enviados)
├── delete_book.py      # Elimina
└── calculate_price.py  # Consulta tasa externa y calcula precio
```

Uso en endpoints:

```python
service: BookUseCase = Depends(BookDeps.get_service)
book = await service.create.execute(data=data)
```

**Dependencias:** La inyeccion esta centralizada en `app/deps.py` con la clase `BookDeps`. Cada endpoint inyecta `BookUseCase` via `Depends()`, y FastAPI resuelve la cadena: sesion DB -> repositorio -> servicio.

## Migraciones

El proyecto usa Alembic con `SQLModel.metadata` como target.

```bash
# Dentro de Docker
docker compose -f docker-compose.local.yml exec server-bookstore-inventory uv run alembic upgrade head

```

La migracion actual crea la tabla `books` con los campos: id, title, author, isbn (unico), cost_usd, selling_price_local, stock_quantity, category, supplier_country, created_at, updated_at.

## Tests

Los tests corren con SQLite en memoria (sin necesitar PostgreSQL). Se usa `aiosqlite` con `StaticPool` para aislar cada test.

```bash
# Todos los tests
docker compose -f docker-compose.local.yml exec server-bookstore-inventory uv run pytest -v

```

Estructura de tests:

```
tests/
├── conftest.py                    # Fixtures compartidas
├── repositories/
│   └── test_book_repository.py    # Tests de acceso a datos
└── services/
    ├── test_create_book.py        # Crear libro (exitoso, ISBN duplicado, validaciones)
    ├── test_get_book.py           # Consultas (por ID, paginado, categoria, bajo stock)
    ├── test_update_book.py        # Actualizar (campos individuales, validaciones)
    ├── test_delete_book.py        # Eliminar (exitoso, no existe)
    └── test_calculate_price.py    # Calculo de precio (exitoso, API falla)
```

27 tests en total. Todos async con `pytest-asyncio`.

## Notas tecnicas

**Por que SQLModel?** Combina SQLAlchemy ORM y Pydantic schemas en un solo modelo. Evita duplicar la definicion de campos entre la tabla y el schema de la API. Para un proyecto de este tamaño es perfecto.

**Por que uv?** Resuelve e instala dependencias mas rapido que pip, genera un lockfile reproducible y reemplaza pip + venv + virtualenv en un solo binario. El Dockerfile usa uv multi-stage para una imagen final mas liviana.

**Calculo de precio:** El endpoint `/calculate-price` consulta una API externa para obtener la tasa de cambio USD -> moneda local. El calculo es: `cost_local = cost_usd * exchange_rate`, luego se aplica un margen del 40%: `selling_price = cost_local * 1.40`. Si la API externa falla, se retorna un error 503 sin fallback automatico. La decision fue intencional: preferir un error claro a un precio con tasa potencialmente desactualizada.

**Validaciones:** Estan en el service, no en el schema. Pydantic solo define la estructura del dato (tipos, longitud maxima). Las reglas de negocio (ISBN duplicado, costo mayor a cero, stock no negativo) se validan en los casos de uso. Esto permite que las mismas reglas se apliquen independientemente de como lleguen los datos.

**Update parcial:** `BookUpdate` tiene todos los campos opcionales. El caso de uso usa `model_dump(exclude_unset=True)` para aplicar solo los campos que el cliente envio. Si no envia ninguno, el libro no cambia. Es perfecto para que llevar un log donde se escriba que fue lo que cambio el usuario unica y exlucivamente

**Algunos problemas:** Se tuvo un par de problemas con la imagen del docker file de postgres dado a la aquitectura de mi maquina (Macbook Pro M1 Pro) esto fue lo que mas retraso me dio, llevandome incluso a que primero hiciera todos los endpoints y luego que resolviera el problema poder probarlos y comenzar a depurar
