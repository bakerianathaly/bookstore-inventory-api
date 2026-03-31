from fastapi import Depends
from sqlmodel import Session

from app.db.sessions import get_db
from app.repositories.permissions_repository import PermissionsRepository
from app.services.permissions import PermissionsUseCase


class PermissionsDeps:
    @staticmethod
    def get_repository(db: Session = Depends(get_db)) -> PermissionsRepository:
        return PermissionsRepository(db)

    @staticmethod
    def get_service(
        repo: PermissionsRepository = Depends(get_repository),
    ) -> PermissionsUseCase:
        return PermissionsUseCase(repo)
