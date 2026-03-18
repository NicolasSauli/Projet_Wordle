from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    email: EmailStr
    nom: str
    prenom: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    email: str
    nom: str
    prenom: str


class StatsResponse(BaseModel):
    victoires: int = 0
    parties: int = 0
    meilleurScore: int = 0
