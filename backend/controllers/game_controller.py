import random
from fastapi import HTTPException
from database import users_db, lobbies_db, games_db, stats_db, generate_game_id, MOTS_DISPONIBLES


def _corriger_guess(mot_secret: str, guess: str) -> list[dict]:
    """Retourne la correction lettre par lettre (correct / present / absent)."""
    result = []
    lettres_secret = list(mot_secret)
    guess_upper = guess.upper()
    lettres_utilisees = lettres_secret.copy()
    temp = [None] * len(guess_upper)

    # 1ère passe : positions correctes (vert)
    for i in range(len(guess_upper)):
        if i < len(lettres_secret) and guess_upper[i] == lettres_secret[i]:
            temp[i] = "correct"
            lettres_utilisees[i] = None

    # 2ème passe : présent mais mal placé (jaune) ou absent (gris)
    for i in range(len(guess_upper)):
        if temp[i] is None:
            lettre = guess_upper[i]
            if lettre in lettres_utilisees:
                idx = lettres_utilisees.index(lettre)
                temp[i] = "present"
                lettres_utilisees[idx] = None
            else:
                temp[i] = "absent"

    for i, lettre in enumerate(guess_upper):
        result.append({"lettre": lettre, "etat": temp[i]})
    return result


def start_game(email: str, lobby_code: str) -> dict:
    if email not in users_db:
        raise HTTPException(status_code=404, detail="User not found")

    lobby = lobbies_db.get(lobby_code)

    # Tous les joueurs du même lobby partagent le même mot
    if lobby and lobby.get("mot_secret"):
        mot_secret = lobby["mot_secret"]
    else:
        mot_secret = random.choice(MOTS_DISPONIBLES)
        if lobby:
            lobby["mot_secret"] = mot_secret
            lobby["started"] = True

    game_id = generate_game_id()
    games_db[game_id] = {
        "mot_secret": mot_secret,
        "email": email,
        "lobby_code": lobby_code,
        "tentatives": [],
        "termine": False,
        "gagne": False,
    }
    return {"game_id": game_id, "longueur": len(mot_secret), "tentatives_restantes": 6}


def submit_guess(game_id: str, guess: str, email: str) -> dict:
    if game_id not in games_db:
        raise HTTPException(status_code=404, detail="Game not found")

    game = games_db[game_id]
    if game["termine"]:
        raise HTTPException(status_code=400, detail="Game is already over")

    mot_secret = game["mot_secret"]
    guess = guess.upper()

    if len(guess) != len(mot_secret):
        raise HTTPException(status_code=400, detail=f"Guess must be {len(mot_secret)} letters")

    correction = _corriger_guess(mot_secret, guess)
    game["tentatives"].append({"mot": guess, "correction": correction})

    gagne = all(c["etat"] == "correct" for c in correction)
    perdu = len(game["tentatives"]) >= 6 and not gagne

    response = {
        "correction": correction,
        "gagne": gagne,
        "perdu": perdu,
        "tentatives_restantes": 6 - len(game["tentatives"]),
        "mot_secret": None,
        "score": None,
    }

    if gagne or perdu:
        game["termine"] = True
        game["gagne"] = gagne

        if email in stats_db:
            stats_db[email]["parties"] += 1
            if gagne:
                stats_db[email]["victoires"] += 1
                score = max(0, 100 - (len(game["tentatives"]) - 1) * 15)
                stats_db[email]["meilleurScore"] = max(stats_db[email]["meilleurScore"], score)
                response["score"] = score

                # Mise à jour du score dans le lobby
                lobby_code = game["lobby_code"]
                if lobby_code in lobbies_db:
                    for joueur in lobbies_db[lobby_code]["joueurs"]:
                        if joueur["email"] == email:
                            joueur["score"] += score
                            break

        if perdu:
            response["mot_secret"] = mot_secret

    return response


def get_game(game_id: str) -> dict:
    if game_id not in games_db:
        raise HTTPException(status_code=404, detail="Game not found")
    game = games_db[game_id]
    return {
        "longueur": len(game["mot_secret"]),
        "tentatives": game["tentatives"],
        "termine": game["termine"],
        "gagne": game["gagne"],
        "tentatives_restantes": 6 - len(game["tentatives"]),
    }
