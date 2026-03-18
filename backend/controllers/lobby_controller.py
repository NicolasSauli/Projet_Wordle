from fastapi import HTTPException
from database import users_db, lobbies_db, generate_lobby_code


def create_lobby(nom: str, email: str) -> dict:
    if email not in users_db:
        raise HTTPException(status_code=404, detail="User not found")

    code = generate_lobby_code()
    while code in lobbies_db:
        code = generate_lobby_code()

    user = users_db[email]
    lobby = {
        "code": code,
        "nom": nom,
        "createur": email,
        "joueurs": [{"email": email, "nom": user["nom"], "score": 0}],
        "started": False,
    }
    lobbies_db[code] = lobby
    return lobby


def join_lobby(code: str, email: str) -> dict:
    if code not in lobbies_db:
        raise HTTPException(status_code=404, detail="Lobby not found")
    if email not in users_db:
        raise HTTPException(status_code=404, detail="User not found")

    lobby = lobbies_db[code]
    user = users_db[email]
    if not any(j["email"] == email for j in lobby["joueurs"]):
        lobby["joueurs"].append({"email": email, "nom": user["nom"], "score": 0})
    return lobby


def get_lobby(code: str) -> dict:
    if code not in lobbies_db:
        raise HTTPException(status_code=404, detail="Lobby not found")
    return lobbies_db[code]


def reset_lobby(code: str) -> dict:
    if code not in lobbies_db:
        raise HTTPException(status_code=404, detail="Lobby not found")

    lobby = lobbies_db[code]
    lobby["started"] = False
    lobby["mot_secret"] = None
    return lobby


def leave_lobby(code: str, email: str) -> dict:
    if code not in lobbies_db:
        raise HTTPException(status_code=404, detail="Lobby not found")

    lobby = lobbies_db[code]
    lobby["joueurs"] = [j for j in lobby["joueurs"] if j["email"] != email]

    if not lobby["joueurs"]:
        del lobbies_db[code]
        return {"message": "Lobby deleted"}
    return {"message": "Left lobby"}
