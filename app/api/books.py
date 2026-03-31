from fastapi import APIRouter, Depends, Response, status

from app.deps import BookDeps
from app.exceptions import (
    BookAlreadyExistsException,
    BookListEmptyException,
    BookNotFoundException,
    ExchangeRateAPIException,
    ValidationException,
)
from app.models.api_response import APIResponse, PaginationInfo
from app.models.book import Book, BookCreate, BookUpdate, PriceCalculationResponse
from app.services.book import BookUseCase

router = APIRouter(prefix="/books", tags=["Books"])


@router.post("/", response_model=APIResponse[Book], status_code=status.HTTP_201_CREATED)
async def crear_libro(
    response: Response,
    data: BookCreate,
    service: BookUseCase = Depends(BookDeps.get_service),
) -> APIResponse[Book]:
    try:
        book = await service.create.execute(data=data)
        return APIResponse(
            success=True, message="El libro fue creado exitosamente", outcome=[book]
        )
    except BookAlreadyExistsException as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return APIResponse(success=False, message=str(e), errors=[str(e)])
    except ValidationException as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return APIResponse(success=False, message=str(e), errors=[str(e)])


@router.get("/", response_model=APIResponse[PaginationInfo])
async def listar_libros(
    response: Response,
    page: int = 1,
    limit: int = 10,
    service: BookUseCase = Depends(BookDeps.get_service),
) -> APIResponse[PaginationInfo]:
    try:
        result = await service.get.listar(page=page, limit=limit)
        return APIResponse(success=True, message="Libros obtenidos", outcome=[result])
    except BookListEmptyException as e:
        response.status_code = status.HTTP_204_NO_CONTENT
        return APIResponse(success=False, message=str(e), errors=[str(e)])


@router.get("/search", response_model=APIResponse[PaginationInfo])
async def buscar_por_categoria(
    response: Response,
    category: str,
    page: int = 1,
    limit: int = 10,
    service: BookUseCase = Depends(BookDeps.get_service),
) -> APIResponse[PaginationInfo]:
    try:
        result = await service.get.buscar_por_categoria(
            category=category, page=page, limit=limit
        )
        return APIResponse(success=True, message="Libros obtenidos", outcome=[result])
    except BookListEmptyException as e:
        response.status_code = status.HTTP_204_NO_CONTENT
        return APIResponse(success=False, message=str(e), errors=[str(e)])


@router.get("/low-stock", response_model=APIResponse[PaginationInfo])
async def libros_bajo_stock(
    response: Response,
    threshold: int = 10,
    page: int = 1,
    limit: int = 10,
    service: BookUseCase = Depends(BookDeps.get_service),
) -> APIResponse[PaginationInfo]:
    try:
        result = await service.get.bajo_stock(
            threshold=threshold, page=page, limit=limit
        )
        return APIResponse(
            success=True, message="Libros con bajo stock obtenidos", outcome=[result]
        )
    except BookListEmptyException as e:
        response.status_code = status.HTTP_204_NO_CONTENT
        return APIResponse(success=False, message=str(e), errors=[str(e)])


@router.get("/{book_id}", response_model=APIResponse[Book])
async def obtener_libro(
    book_id: int,
    response: Response,
    service: BookUseCase = Depends(BookDeps.get_service),
) -> APIResponse[Book]:
    try:
        book = await service.get.obtener(book_id)
        return APIResponse(success=True, message="Libro obtenido", outcome=[book])
    except BookNotFoundException as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return APIResponse(success=False, message=str(e), errors=[str(e)])


@router.put("/{book_id}", response_model=APIResponse[Book])
async def actualizar_libro(
    book_id: int,
    data: BookUpdate,
    response: Response,
    service: BookUseCase = Depends(BookDeps.get_service),
) -> APIResponse[Book]:
    try:
        book = await service.update.execute(book_id, data)
        return APIResponse(success=True, message="Libro actualizado", outcome=[book])
    except BookNotFoundException as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return APIResponse(success=False, message=str(e), errors=[str(e)])
    except (BookAlreadyExistsException, ValidationException) as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return APIResponse(success=False, message=str(e), errors=[str(e)])


@router.delete("/{book_id}", response_model=APIResponse[None])
async def eliminar_libro(
    book_id: int,
    response: Response,
    service: BookUseCase = Depends(BookDeps.get_service),
) -> APIResponse[None]:
    try:
        await service.delete.execute(book_id)
        return APIResponse(
            success=True, message="El libro a sido eliminado exitosamente", outcome=[]
        )
    except BookNotFoundException as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return APIResponse(success=False, message=str(e), errors=[str(e)])


@router.post(
    "/{book_id}/calculate-price",
    response_model=APIResponse[PriceCalculationResponse],
)
async def calcular_precio(
    book_id: int,
    response: Response,
    service: BookUseCase = Depends(BookDeps.get_service),
) -> APIResponse[PriceCalculationResponse]:
    try:
        result = await service.calculate_price.execute(book_id)
        return APIResponse(
            success=True,
            message="Precio calculado exitosamente",
            outcome=[result],
        )
    except BookNotFoundException as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return APIResponse(success=False, message=str(e), errors=[str(e)])
    except ExchangeRateAPIException as e:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return APIResponse(success=False, message=str(e), errors=[str(e)])
