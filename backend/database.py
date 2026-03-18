import hashlib
import random
import string

# ── In-memory storage ──────────────────────────────────────────────────────────
users_db: dict = {}
stats_db: dict = {}
lobbies_db: dict = {}
games_db: dict = {}

# ── Word list ──────────────────────────────────────────────────────────────────
MOTS_DISPONIBLES = [
    "ARBRE", "BOIRE", "CHIEN", "DROIT", "ECOLE",
    "FLEUR", "GRAND", "HIVER", "JOUER", "LIVRE",
    "MAGIE", "NAGER", "ORDRE", "PAINS", "RONDE",
    "TEMPS", "UTILE", "VENIR", "WAGON", "ZONES",
    "MONDE", "BLANC", "ROUGE", "TERRE", "VERRE",
    "CHAUD", "FROID", "PLAGE", "SABLE", "LUNDI",
    "MARDI", "MERCI", "NUITS", "FORME",
]

# ── Utility functions ──────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def generate_lobby_code() -> str:
    return ''.join(random.choices(string.digits, k=6))


def generate_game_id() -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))
