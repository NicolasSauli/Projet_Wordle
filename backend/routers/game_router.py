from fastapi import APIRouter
from models.game import GameStart, GameResponse, GuessSubmit, GuessResponse
from controllers import game_controller

router = APIRouter(prefix="/game", tags=["game"])


@router.post("/start", response_model=GameResponse)
def start(data: GameStart):
    return GameResponse(**game_controller.start_game(data.email, data.lobby_code))


@router.post("/guess", response_model=GuessResponse)
def guess(data: GuessSubmit):
    return GuessResponse(**game_controller.submit_guess(data.game_id, data.guess, data.email))


@router.get("/{game_id}")
def get(game_id: str):
    return game_controller.get_game(game_id)
