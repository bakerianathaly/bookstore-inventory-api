from starlette.config import Config

config = Config(".env")

PROJECT_NAME = "Bookstore Inventory"
DESCRIPTION = "Sistema de gestión de inventario para una cadena de librerías"
DEBUG: bool = False
TIMEZONE: str = "America/Caracas"

VERSION = "1.0.0"
API_PREFIX = "/api/v1"

DATABASE_URL = config("DATABASE_URL", cast=str, default="sqlite+aiosqlite:///./test.db")
DEFAULT_EXCHANGE_RATE = config("DEFAULT_EXCHANGE_RATE", cast=str, default="36.50")
TARGET_CURRENCY = config("TARGET_CURRENCY", cast=str, default="VES")
EXCHANGE_RATE_API_URL = config(
    "EXCHANGE_RATE_API_URL",
    cast=str,
    default="https://api.exchangerate-api.com/v4/latest/USD",
)
