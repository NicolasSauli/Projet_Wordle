# Wordle Multijoueur

Un jeu Wordle multijoueur en francais avec un backend FastAPI et un frontend React.

## Structure du projet

```
Projet_Wordle/
├── backend/
│   ├── main.py           # API FastAPI
│   └── requirements.txt  # Dependances Python
├── frontend/
│   └── index.html        # Application React
├── run.sh                # Script de demarrage (Linux/Mac)
├── run.bat               # Script de demarrage (Windows)
└── README.md
```

## Installation et Lancement

### Windows

**Methode rapide:**
```
Double-cliquez sur run.bat
```

**Methode manuelle:**
```cmd
:: Creer l'environnement virtuel
python -m venv venv

:: Activer l'environnement
venv\Scripts\activate

:: Installer les dependances
pip install -r backend\requirements.txt

:: Terminal 1 - Lancer le backend
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000

:: Terminal 2 - Lancer le frontend
cd frontend
python -m http.server 3000
```

### Linux / Mac

**Methode rapide:**
```bash
chmod +x run.sh
./run.sh
```

**Methode manuelle:**
```bash
# Creer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement
source venv/bin/activate

# Installer les dependances
pip install -r backend/requirements.txt

# Terminal 1 - Lancer le backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 2 - Lancer le frontend
cd frontend
python3 -m http.server 3000
```

## Acceder au jeu

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **Documentation API**: http://localhost:8000/docs

## Fonctionnalites

- **Authentification**: Inscription et connexion des joueurs
- **Lobbies**: Creer ou rejoindre des parties multijoueurs
- **Jeu Wordle**: Devinez le mot de 5 lettres en 6 essais
- **Statistiques**: Suivi des victoires, parties jouees et meilleur score
- **Scores**: Systeme de points (100 points max, -15 par essai supplementaire)

## API Endpoints

| Methode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/auth/register` | Inscription |
| POST | `/auth/login` | Connexion |
| GET | `/stats/{email}` | Statistiques joueur |
| POST | `/lobby/create` | Creer un lobby |
| POST | `/lobby/join` | Rejoindre un lobby |
| GET | `/lobby/{code}` | Info lobby |
| POST | `/game/start` | Demarrer une partie |
| POST | `/game/guess` | Soumettre un essai |

## Technologies

- **Backend**: Python, FastAPI, Pydantic, Uvicorn
- **Frontend**: React 18, Tailwind CSS
- **Stockage**: In-memory (pour demo)
