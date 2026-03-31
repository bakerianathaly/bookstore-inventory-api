class BookNotFoundException(Exception):
    """Libro no encontrado en la base de datos."""

    pass


class BookAlreadyExistsException(Exception):
    """Ya existe un libro con el mismo ISBN."""

    pass


class ValidationException(Exception):
    """Error de validación de datos del negocio."""

    pass


class ExchangeRateAPIException(Exception):
    """Error al llamar la API de tasas de cambio."""

    pass


class BookListEmptyException(Exception):
    """Listado de libros se encuentra vacio."""

    pass
    
class ExchangeRateApiException(Exception):
    """Excepcion para la busqueda de la api."""

    pass
