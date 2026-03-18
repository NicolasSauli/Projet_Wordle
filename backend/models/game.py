from pydantic import BaseModel
from typing import Optional


class GameStart(BaseModel):
    email: str
    lobby_code: str


class GameResponse(BaseModel):
    game_id: str
    longueur: int
    tentatives_restantes: int


class GuessSubmit(BaseModel):
    game_id: str
    guess: str
    email: str


class LetterResult(BaseModel):
    lettre: str
    etat: str  # 'correct' | 'present' | 'absent'


class GuessResponse(BaseModel):
    correction: list[LetterResult]
    gagne: bool
    perdu: bool
    mot_secret: Optional[str] = None
    score: Optional[int] = None
    tentatives_restantes: int
