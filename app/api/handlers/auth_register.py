from fastapi import APIRouter, Depends

from app.database.deps import get_session
from app.schemas.auth import RegisterRequest, RegisterResponse
from app.services.auth_service import AuthService

router = APIRouter(tags=["Auth"])


@router.post("/auth/register", response_model=RegisterResponse, status_code=201)
async def register_user(
    data: RegisterRequest,
    session=Depends(get_session),
):
    service = AuthService(session)

    user = await service.register(
        username=data.username,
        email=str(data.email),
        password=data.password,
    )

    return RegisterResponse(
        id=user.id,
        username=user.username,
        email=user.email,
    )
