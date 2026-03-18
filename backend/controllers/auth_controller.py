from fastapi import HTTPException
from database import users_db, stats_db, hash_password


def register_user(email: str, nom: str, prenom: str, password: str) -> dict:
    if email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    users_db[email] = {
        "email": email,
        "nom": nom,
        "prenom": prenom,
        "password": hash_password(password),
    }
    stats_db[email] = {"victoires": 0, "parties": 0, "meilleurScore": 0}
    return users_db[email]


def login_user(email: str, password: str) -> dict:
    if email not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    if users_db[email]["password"] != hash_password(password):
        raise HTTPException(status_code=401, detail="Invalid password")
    return users_db[email]


def get_stats(email: str) -> dict:
    return stats_db.get(email, {"victoires": 0, "parties": 0, "meilleurScore": 0})
