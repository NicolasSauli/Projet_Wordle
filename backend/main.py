from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
import random
import string
from datetime import datetime
import hashlib

app = FastAPI(title="Wordle API", version="1.0.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# French words list
MOTS_DISPONIBLES = [
    "ARBRE", "BOIRE", "CHIEN", "DROIT", "ECOLE",
    "FLEUR", "GRAND", "HIVER", "JOUER", "LIVRE",
    "MAGIE", "NAGER", "ORDRE", "PAINS", "RONDE",
    "TEMPS", "UTILE", "VENIR", "WAGON", "ZONES",
    "MONDE", "BLANC", "ROUGE", "TERRE", "VERRE",
    "CHAUD", "FROID", "PLAGE", "SOLEIL".replace("SOLEIL", "SABLE"),
    "LUNDI", "MARDI", "MERCI", "NUITS", "FORME"
]

# In-memory storage (replace with database in production)
users_db = {}
stats_db = {}
lobbies_db = {}
games_db = {}


# Pydantic models
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
    etat: str  # 'correct', 'present', 'absent'


class GuessResponse(BaseModel):
    correction: list[LetterResult]
    gagne: bool
    perdu: bool
    mot_secret: Optional[str] = None
    score: Optional[int] = None
    tentatives_restantes: int


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def generate_lobby_code() -> str:
    return ''.join(random.choices(string.digits, k=6))


def generate_game_id() -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))


def corriger_guess(mot_secret: str, guess: str) -> list[dict]:
    result = []
    lettres_secrets = list(mot_secret)
    guess_upper = guess.upper()
    lettres_utilisees = lettres_secrets.copy()
    temp_result = [None] * len(guess_upper)

    # First pass: correct positions (green)
    for i in range(len(guess_upper)):
        if i < len(lettres_secrets) and guess_upper[i] == lettres_secrets[i]:
            temp_result[i] = 'correct'
            lettres_utilisees[i] = None

    # Second pass: present but wrong position (yellow) and absent (gray)
    for i in range(len(guess_upper)):
        if temp_result[i] is None:
            lettre = guess_upper[i]
            if lettre in lettres_utilisees:
                idx = lettres_utilisees.index(lettre)
                temp_result[i] = 'present'
                lettres_utilisees[idx] = None
            else:
                temp_result[i] = 'absent'

    for i, lettre in enumerate(guess_upper):
        result.append({"lettre": lettre, "etat": temp_result[i]})

    return result


# Routes
@app.get("/")
def root():
    return {"message": "Wordle API is running"}


@app.post("/auth/register", response_model=UserResponse)
def register(user: UserRegister):
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")

    users_db[user.email] = {
        "email": user.email,
        "nom": user.nom,
        "prenom": user.prenom,
        "password": hash_password(user.password)
    }
    stats_db[user.email] = {"victoires": 0, "parties": 0, "meilleurScore": 0}

    return UserResponse(email=user.email, nom=user.nom, prenom=user.prenom)


@app.post("/auth/login", response_model=UserResponse)
def login(user: UserLogin):
    if user.email not in users_db:
        raise HTTPException(status_code=404, detail="User not found")

    if users_db[user.email]["password"] != hash_password(user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    db_user = users_db[user.email]
    return UserResponse(email=db_user["email"], nom=db_user["nom"], prenom=db_user["prenom"])


@app.get("/stats/{email}", response_model=StatsResponse)
def get_stats(email: str):
    if email not in stats_db:
        return StatsResponse()
    return StatsResponse(**stats_db[email])


@app.post("/lobby/create", response_model=LobbyResponse)
def create_lobby(data: LobbyCreate):
    if data.email not in users_db:
        raise HTTPException(status_code=404, detail="User not found")

    code = generate_lobby_code()
    while code in lobbies_db:
        code = generate_lobby_code()

    user = users_db[data.email]
    lobby = {
        "code": code,
        "nom": data.nom,
        "createur": data.email,
        "joueurs": [{"email": data.email, "nom": user["nom"], "score": 0}]
    }
    lobbies_db[code] = lobby

    return LobbyResponse(**lobby)


@app.post("/lobby/join", response_model=LobbyResponse)
def join_lobby(data: LobbyJoin):
    if data.code not in lobbies_db:
        raise HTTPException(status_code=404, detail="Lobby not found")

    if data.email not in users_db:
        raise HTTPException(status_code=404, detail="User not found")

    lobby = lobbies_db[data.code]
    user = users_db[data.email]

    # Check if already in lobby
    if not any(j["email"] == data.email for j in lobby["joueurs"]):
        lobby["joueurs"].append({"email": data.email, "nom": user["nom"], "score": 0})

    return LobbyResponse(**lobby)


@app.get("/lobby/{code}", response_model=LobbyResponse)
def get_lobby(code: str):
    if code not in lobbies_db:
        raise HTTPException(status_code=404, detail="Lobby not found")
    return LobbyResponse(**lobbies_db[code])


@app.post("/lobby/{code}/leave")
def leave_lobby(code: str, email: str):
    if code not in lobbies_db:
        raise HTTPException(status_code=404, detail="Lobby not found")

    lobby = lobbies_db[code]
    lobby["joueurs"] = [j for j in lobby["joueurs"] if j["email"] != email]

    # Delete lobby if empty
    if not lobby["joueurs"]:
        del lobbies_db[code]
        return {"message": "Lobby deleted"}

    return {"message": "Left lobby"}


@app.post("/game/start", response_model=GameResponse)
def start_game(data: GameStart):
    if data.email not in users_db:
        raise HTTPException(status_code=404, detail="User not found")

    mot_secret = random.choice(MOTS_DISPONIBLES)
    game_id = generate_game_id()

    games_db[game_id] = {
        "mot_secret": mot_secret,
        "email": data.email,
        "lobby_code": data.lobby_code,
        "tentatives": [],
        "termine": False,
        "gagne": False
    }

    return GameResponse(
        game_id=game_id,
        longueur=len(mot_secret),
        tentatives_restantes=6
    )


@app.post("/game/guess", response_model=GuessResponse)
def submit_guess(data: GuessSubmit):
    if data.game_id not in games_db:
        raise HTTPException(status_code=404, detail="Game not found")

    game = games_db[data.game_id]

    if game["termine"]:
        raise HTTPException(status_code=400, detail="Game is already over")

    mot_secret = game["mot_secret"]
    guess = data.guess.upper()

    if len(guess) != len(mot_secret):
        raise HTTPException(status_code=400, detail=f"Guess must be {len(mot_secret)} letters")

    correction = corriger_guess(mot_secret, guess)
    game["tentatives"].append({"mot": guess, "correction": correction})

    gagne = all(c["etat"] == "correct" for c in correction)
    perdu = len(game["tentatives"]) >= 6 and not gagne

    response = GuessResponse(
        correction=correction,
        gagne=gagne,
        perdu=perdu,
        tentatives_restantes=6 - len(game["tentatives"])
    )

    if gagne or perdu:
        game["termine"] = True
        game["gagne"] = gagne

        # Update stats
        email = game["email"]
        if email in stats_db:
            stats_db[email]["parties"] += 1
            if gagne:
                stats_db[email]["victoires"] += 1
                score = max(0, 100 - (len(game["tentatives"]) - 1) * 15)
                stats_db[email]["meilleurScore"] = max(stats_db[email]["meilleurScore"], score)
                response.score = score

                # Update lobby score
                lobby_code = game["lobby_code"]
                if lobby_code in lobbies_db:
                    lobby = lobbies_db[lobby_code]
                    for joueur in lobby["joueurs"]:
                        if joueur["email"] == email:
                            joueur["score"] += score
                            break

        if perdu:
            response.mot_secret = mot_secret

    return response


@app.get("/game/{game_id}")
def get_game(game_id: str):
    if game_id not in games_db:
        raise HTTPException(status_code=404, detail="Game not found")

    game = games_db[game_id]
    return {
        "longueur": len(game["mot_secret"]),
        "tentatives": game["tentatives"],
        "termine": game["termine"],
        "gagne": game["gagne"],
        "tentatives_restantes": 6 - len(game["tentatives"])
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
