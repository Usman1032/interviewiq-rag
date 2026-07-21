from fastapi import APIRouter
from typing import List

from app.config import SUPPORTED_ROLES
from app.schemas import RoleOut

router = APIRouter(prefix="/api/roles", tags=["roles"])


@router.get("", response_model=List[RoleOut])
def list_roles():
    return [{"key": k, "label": v} for k, v in SUPPORTED_ROLES.items()]
