from fastapi import APIRouter
from models.user import UserRegister, UserLogin, UserResponse, StatsResponse
from controllers.auth_controller import register_user, login_user, get_stats

router = APIRouter(tags=["auth"])


@router.post("/auth/register", response_model=UserResponse)
def register(user: UserRegister):
    data = register_user(user.email, user.nom, user.prenom, user.password)
    return UserResponse(email=data["email"], nom=data["nom"], prenom=data["prenom"])


@router.post("/auth/login", response_model=UserResponse)
def login(user: UserLogin):
    data = login_user(user.email, user.password)
    return UserResponse(email=data["email"], nom=data["nom"], prenom=data["prenom"])


@router.get("/stats/{email}", response_model=StatsResponse)
def stats(email: str):
    return StatsResponse(**get_stats(email))
