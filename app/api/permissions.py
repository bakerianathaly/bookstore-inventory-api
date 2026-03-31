from typing import Optional
from fastapi import APIRouter, Depends, Response, status

from app.deps import PermissionsDeps
from app.models.api_response import APIResponse, PaginationInfo
from app.models.permissions import Permissions, PermissionsCreate
from app.services.permissions import PermissionsUseCase

router = APIRouter(prefix="/permissions", tags=["Permisos - CRUD"])


@router.post(
    "/", response_model=APIResponse[Permissions], status_code=status.HTTP_201_CREATED
)
async def crear_permiso(
    response: Response,
    permiso: PermissionsCreate,
    service: PermissionsUseCase = Depends(PermissionsDeps.get_service),
) -> APIResponse[Permissions]:
    try:
        outcome = await service.create_new_permissions.execute(permiso)
        return APIResponse(success=True, message="Permiso creado", outcome=[outcome])
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return APIResponse(
            success=False,
            message=f"Error al intentar crear el permiso: {str(e)}.",
            errors=[str(e)],
        )


@router.get("/", response_model=APIResponse[PaginationInfo])
async def listar_permisos(
    page: int = 1,
    limit: int = 10,
    is_active: Optional[str] = "",
    service: PermissionsUseCase = Depends(PermissionsDeps.get_service),
) -> APIResponse[PaginationInfo]:
    try:
        result = await service.leer.listar(page=page, limit=limit, is_active=is_active)

        return APIResponse(
            success=True,
            message="Se obtuvieron todos los permisos exitosamente",
            outcome=[result],
        )
    except ValueError as e:
        return APIResponse(success=False, message=str(e), errors=[str(e)])


# @router.get("/{permiso_id}", response_model=APIResponse[Permissions])
# async def obtener_permiso(
#     permiso_id: UUID,
#     service: PermissionsUseCase = Depends(PermissionsDeps.get_service),
# ) -> APIResponse[Permissions]:
#     permiso = await service.leer.obtener(permiso_id)
#     if not permiso:
#         return APIResponse(
#             success=False,
#             message="Permiso no encontrado",
#             errors=["Permiso no encontrado"],
#         )
#     return APIResponse(success=True, message="Permiso obtenido", outcome=[permiso])


# @router.delete("/{permiso_id}", response_model=APIResponse[None])
# async def eliminar_permiso(
#     permiso_id: UUID,
#     service: PermissionsUseCase = Depends(PermissionsDeps.get_service),
# ) -> APIResponse[None]:
#     resultado = await service.eliminar.execute(permiso_id)
#     if not resultado:
#         return APIResponse(
#             success=False,
#             message="Permiso no encontrado",
#             errors=["Permiso no encontrado"],
#         )
#     return APIResponse(success=True, message="Permiso eliminado", outcome=[])
