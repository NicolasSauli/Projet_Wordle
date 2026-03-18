from pydantic import BaseModel


class LobbyCreate(BaseModel):
    nom: str
    email: str


class LobbyJoin(BaseModel):
    code: str
    email: str


class JoueurLobby(BaseModel):
    email: str
    nom: str
    score: int = 0


class LobbyResponse(BaseModel):
    code: str
    nom: str
    createur: str
    joueurs: list[JoueurLobby]
    started: bool = False
