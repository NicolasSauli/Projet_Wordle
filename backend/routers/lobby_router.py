from fastapi import APIRouter
from models.lobby import LobbyCreate, LobbyJoin, LobbyResponse
from controllers import lobby_controller

router = APIRouter(prefix="/lobby", tags=["lobby"])


@router.post("/create", response_model=LobbyResponse)
def create(data: LobbyCreate):
    return LobbyResponse(**lobby_controller.create_lobby(data.nom, data.email))


@router.post("/join", response_model=LobbyResponse)
def join(data: LobbyJoin):
    return LobbyResponse(**lobby_controller.join_lobby(data.code, data.email))


@router.get("/{code}", response_model=LobbyResponse)
def get(code: str):
    return LobbyResponse(**lobby_controller.get_lobby(code))


@router.post("/{code}/reset")
def reset(code: str):
    return LobbyResponse(**lobby_controller.reset_lobby(code))


@router.post("/{code}/leave")
def leave(code: str, email: str):
    return lobby_controller.leave_lobby(code, email)
