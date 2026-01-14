from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
import random
import string
import json
import hashlib
import asyncio

app = FastAPI(title="Wordle API", version="2.0.0")

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
    "CHAUD", "FROID", "PLAGE", "SABLE", "FORME",
    "LUNDI", "MARDI", "MERCI", "NUITS", "PIANO"
]

# In-memory storage
users_db = {}
stats_db = {}
lobbies_db = {}


# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        # lobby_code -> {email -> WebSocket}
        self.active_connections: dict[str, dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, lobby_code: str, email: str):
        await websocket.accept()
        if lobby_code not in self.active_connections:
            self.active_connections[lobby_code] = {}
        self.active_connections[lobby_code][email] = websocket

    def disconnect(self, lobby_code: str, email: str):
        if lobby_code in self.active_connections:
            if email in self.active_connections[lobby_code]:
                del self.active_connections[lobby_code][email]
            if not self.active_connections[lobby_code]:
                del self.active_connections[lobby_code]

    async def broadcast_to_lobby(self, lobby_code: str, message: dict, exclude_email: str = None):
        if lobby_code in self.active_connections:
            for email, ws in self.active_connections[lobby_code].items():
                if email != exclude_email:
                    try:
                        await ws.send_json(message)
                    except:
                        pass

    async def send_to_player(self, lobby_code: str, email: str, message: dict):
        if lobby_code in self.active_connections:
            if email in self.active_connections[lobby_code]:
                try:
                    await self.active_connections[lobby_code][email].send_json(message)
                except:
                    pass


manager = ConnectionManager()


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
    en_jeu: bool = False
    mot_longueur: Optional[int] = None


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def generate_lobby_code() -> str:
    return ''.join(random.choices(string.digits, k=6))


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


# REST Routes
@app.get("/")
def root():
    return {"message": "Wordle API v2.0 with WebSockets"}


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
        "joueurs": [{"email": data.email, "nom": user["nom"], "score": 0}],
        "en_jeu": False,
        "mot_secret": None,
        "mot_longueur": None,
        "joueurs_finis": [],
        "joueurs_state": {}  # email -> {tentatives: [], termine: bool, gagne: bool}
    }
    lobbies_db[code] = lobby

    return LobbyResponse(**{k: v for k, v in lobby.items() if k in LobbyResponse.model_fields})


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

    return LobbyResponse(**{k: v for k, v in lobby.items() if k in LobbyResponse.model_fields})


@app.get("/lobby/{code}", response_model=LobbyResponse)
def get_lobby(code: str):
    if code not in lobbies_db:
        raise HTTPException(status_code=404, detail="Lobby not found")
    lobby = lobbies_db[code]
    return LobbyResponse(**{k: v for k, v in lobby.items() if k in LobbyResponse.model_fields})


# WebSocket endpoint
@app.websocket("/ws/{lobby_code}/{email}")
async def websocket_endpoint(websocket: WebSocket, lobby_code: str, email: str):
    if lobby_code not in lobbies_db:
        await websocket.close(code=4004)
        return

    if email not in users_db:
        await websocket.close(code=4001)
        return

    await manager.connect(websocket, lobby_code, email)
    lobby = lobbies_db[lobby_code]
    user = users_db[email]

    # Notify others that player joined
    await manager.broadcast_to_lobby(lobby_code, {
        "type": "player_joined",
        "email": email,
        "nom": user["nom"],
        "joueurs": lobby["joueurs"]
    }, exclude_email=email)

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "start_game":
                # Only creator can start
                if email == lobby["createur"]:
                    mot_secret = random.choice(MOTS_DISPONIBLES)
                    lobby["mot_secret"] = mot_secret
                    lobby["mot_longueur"] = len(mot_secret)
                    lobby["en_jeu"] = True
                    lobby["joueurs_finis"] = []
                    lobby["joueurs_state"] = {}

                    # Initialize state for all players
                    for joueur in lobby["joueurs"]:
                        lobby["joueurs_state"][joueur["email"]] = {
                            "tentatives": [],
                            "termine": False,
                            "gagne": False
                        }

                    # Broadcast game start to all players
                    await manager.broadcast_to_lobby(lobby_code, {
                        "type": "game_started",
                        "longueur": len(mot_secret)
                    })

            elif msg_type == "guess":
                if not lobby["en_jeu"]:
                    continue

                guess = data.get("guess", "").upper()
                mot_secret = lobby["mot_secret"]

                if len(guess) != len(mot_secret):
                    await manager.send_to_player(lobby_code, email, {
                        "type": "error",
                        "message": f"Le mot doit faire {len(mot_secret)} lettres"
                    })
                    continue

                player_state = lobby["joueurs_state"].get(email)
                if not player_state or player_state["termine"]:
                    continue

                # Process guess
                correction = corriger_guess(mot_secret, guess)
                player_state["tentatives"].append({
                    "mot": guess,
                    "correction": correction
                })

                gagne = all(c["etat"] == "correct" for c in correction)
                perdu = len(player_state["tentatives"]) >= 6 and not gagne

                # Send result to player
                result = {
                    "type": "guess_result",
                    "correction": correction,
                    "gagne": gagne,
                    "perdu": perdu,
                    "tentatives_count": len(player_state["tentatives"])
                }

                if gagne:
                    score = max(0, 100 - (len(player_state["tentatives"]) - 1) * 15)
                    result["score"] = score
                    player_state["termine"] = True
                    player_state["gagne"] = True
                    lobby["joueurs_finis"].append(email)

                    # Update stats
                    if email in stats_db:
                        stats_db[email]["parties"] += 1
                        stats_db[email]["victoires"] += 1
                        stats_db[email]["meilleurScore"] = max(stats_db[email]["meilleurScore"], score)

                    # Update lobby score
                    for joueur in lobby["joueurs"]:
                        if joueur["email"] == email:
                            joueur["score"] += score
                            break

                elif perdu:
                    result["mot_secret"] = mot_secret
                    player_state["termine"] = True
                    player_state["gagne"] = False
                    lobby["joueurs_finis"].append(email)

                    # Update stats
                    if email in stats_db:
                        stats_db[email]["parties"] += 1

                await manager.send_to_player(lobby_code, email, result)

                # Broadcast progress to others (without revealing letters)
                await manager.broadcast_to_lobby(lobby_code, {
                    "type": "player_progress",
                    "email": email,
                    "nom": user["nom"],
                    "tentatives_count": len(player_state["tentatives"]),
                    "termine": player_state["termine"],
                    "gagne": player_state["gagne"]
                }, exclude_email=email)

                # Check if all players finished
                all_finished = all(
                    lobby["joueurs_state"].get(j["email"], {}).get("termine", False)
                    for j in lobby["joueurs"]
                )

                if all_finished:
                    lobby["en_jeu"] = False
                    # Build final results
                    results = []
                    for joueur in lobby["joueurs"]:
                        state = lobby["joueurs_state"].get(joueur["email"], {})
                        results.append({
                            "email": joueur["email"],
                            "nom": joueur["nom"],
                            "gagne": state.get("gagne", False),
                            "tentatives": len(state.get("tentatives", [])),
                            "score": joueur["score"]
                        })

                    # Sort by: winners first, then by fewer attempts
                    results.sort(key=lambda x: (not x["gagne"], x["tentatives"]))

                    await manager.broadcast_to_lobby(lobby_code, {
                        "type": "game_ended",
                        "mot_secret": mot_secret,
                        "results": results,
                        "joueurs": lobby["joueurs"]
                    })

            elif msg_type == "chat":
                # Optional: chat messages
                message = data.get("message", "")
                await manager.broadcast_to_lobby(lobby_code, {
                    "type": "chat",
                    "email": email,
                    "nom": user["nom"],
                    "message": message
                })

    except WebSocketDisconnect:
        manager.disconnect(lobby_code, email)
        # Notify others
        await manager.broadcast_to_lobby(lobby_code, {
            "type": "player_left",
            "email": email,
            "nom": user["nom"]
        })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
