from typing import Optional, Tuple

from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permissions import Permissions


class PermissionsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, new_permission: Permissions) -> Permissions:
        try:
            self.db.add(new_permission)
            await self.db.commit()
            await self.db.refresh(new_permission)
            return new_permission
        except Exception as e:
            await self.db.rollback()
            raise Exception(f"Error al crear permiso: {str(e)}") from e

    async def get_permissions_by_code(self, code: str) -> Optional[Permissions]:
        statement = select(Permissions).where(Permissions.permission_code == code)
        result = await self.db.exec(statement)
        return result.one_or_none()

    async def get_all_paginated(
        self, is_active: str, page: int = 1, limit: int = 10
    ) -> Tuple:
        offset = (page - 1) * limit
        query_base = select(
            Permissions.id,
            Permissions.functionality,
            Permissions.permission_code,
            Permissions.is_active,
            Permissions.descripcion,
        )
        query_conditions = []
        # FALTA AGREGAR VALIDACION PARA QUE LEVANTE UNA EXCEPCION SI NO HAY NADA QUE LISTAR PARA EL 204
        if is_active != "":
            value = True if is_active == "True" else False
            print(value)
            query_conditions.append(Permissions.is_active == value)

        result = self.db.exec(
            query_base.where(and_(*query_conditions))
            .order_by(Permissions.descripcion)
            .group_by(
                Permissions.functionality,
                Permissions.descripcion,
                Permissions.id,
                Permissions.permission_code,
                Permissions.is_active,
            )
            .offset(offset)
            .limit(limit)
        )
        permissions = list(result.all())
        permissions = [dict(x._mapping) for x in permissions]

        count_statement = select(func.count()).select_from(Permissions)
        count_result = self.db.exec(count_statement.where(and_(*query_conditions)))
        total_records = count_result.one()[0]

        return permissions, total_records

    # async def delete(self, permission_id: UUID) -> bool:
    #     permission = await self.get_by_id(permission_id)
    #     if permission:
    #         await self.db.delete(permission)
    #         await self.db.commit()
    #         return True
    #     return False

    # async def get_by_id(self, permission_id: UUID) -> Optional[Permissions]:
    #     statement = select(Permissions).where(Permissions.id == permission_id)
    #     result = await self.db.exec(statement)
    #     return result.one_or_none()
