// ── Model : accès aux données via l'API REST ───────────────────────────────────
const API_URL = 'http://172.20.4.238:8000';

const api = {
    async _fetch(path, options = {}) {
        const res = await fetch(`${API_URL}${path}`, {
            headers: { 'Content-Type': 'application/json' },
            ...options,
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Erreur serveur');
        }
        return res.json();
    },

    register(email, nom, prenom, password) {
        return this._fetch('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ email, nom, prenom, password }),
        });
    },

    login(email, password) {
        return this._fetch('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });
    },

    getStats(email) {
        return this._fetch(`/stats/${email}`);
    },

    createLobby(nom, email) {
        return this._fetch('/lobby/create', {
            method: 'POST',
            body: JSON.stringify({ nom, email }),
        });
    },

    joinLobby(code, email) {
        return this._fetch('/lobby/join', {
            method: 'POST',
            body: JSON.stringify({ code, email }),
        });
    },

    getLobby(code) {
        return this._fetch(`/lobby/${code}`);
    },

    resetLobby(code) {
        return this._fetch(`/lobby/${code}/reset`, { method: 'POST' });
    },

    startGame(email, lobby_code) {
        return this._fetch('/game/start', {
            method: 'POST',
            body: JSON.stringify({ email, lobby_code }),
        });
    },

    submitGuess(game_id, guess, email) {
        return this._fetch('/game/guess', {
            method: 'POST',
            body: JSON.stringify({ game_id, guess, email }),
        });
    },
};
