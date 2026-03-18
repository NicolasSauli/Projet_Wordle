// ── Controller : gestion de l'état et des actions ────────────────────────────

const WordleApp = () => {
    const [page, setPage] = React.useState('home');
    const [user, setUser] = React.useState(null);
    const [lobby, setLobby] = React.useState(null);
    const [gameId, setGameId] = React.useState(null);
    const [wordLength, setWordLength] = React.useState(5);
    const [tentatives, setTentatives] = React.useState([]);
    const [currentGuess, setCurrentGuess] = React.useState('');
    const [message, setMessage] = React.useState('');
    const [messageType, setMessageType] = React.useState('info');
    const [stats, setStats] = React.useState({ victoires: 0, parties: 0, meilleurScore: 0 });
    const [gameOver, setGameOver] = React.useState(false);
    const [loading, setLoading] = React.useState(false);
    const prevStartedRef = React.useRef(false);

    // ── Init : restauration session ────────────────────────────────────────────
    React.useEffect(() => {
        const saved = localStorage.getItem('wordleUser');
        if (saved) {
            const u = JSON.parse(saved);
            setUser(u);
            loadStats(u.email);
            setPage('menu');
        }
    }, []);

    // ── Polling lobby (salle d'attente) ───────────────────────────────────────
    React.useEffect(() => {
        if (page !== 'lobby' || !lobby) return;
        prevStartedRef.current = lobby.started; // initialise avec l'état actuel au retour
        const code = lobby.code;
        const interval = setInterval(async () => {
            try {
                const data = await api.getLobby(code);
                const wasStarted = prevStartedRef.current;
                prevStartedRef.current = data.started;
                setLobby(data);
                // Ne démarre la partie que sur une transition false → true
                if (data.started && !wasStarted && user.email !== data.createur) {
                    clearInterval(interval);
                    await doStartGame(user.email, code);
                }
            } catch (_) {}
        }, 2000);
        return () => clearInterval(interval);
    }, [page]);

    // ── Polling scores pendant la partie ─────────────────────────────────────
    React.useEffect(() => {
        if (page !== 'jeu' || !lobby) return;
        const code = lobby.code;
        const interval = setInterval(async () => {
            try {
                const data = await api.getLobby(code);
                setLobby(data);
            } catch (_) {}
        }, 3000);
        return () => clearInterval(interval);
    }, [page]);

    // ── Clavier physique ──────────────────────────────────────────────────────
    React.useEffect(() => {
        const onKey = (e) => {
            if (page !== 'jeu' || gameOver) return;
            if (e.key === 'Enter') handleKeyPress('ENTER');
            else if (e.key === 'Backspace') handleKeyPress('BACK');
            else if (/^[a-zA-Z]$/.test(e.key)) handleKeyPress(e.key.toUpperCase());
        };
        window.addEventListener('keydown', onKey);
        return () => window.removeEventListener('keydown', onKey);
    }, [page, gameOver, currentGuess, wordLength, tentatives, gameId, user]);

    // ── Helpers ────────────────────────────────────────────────────────────────
    const showMessage = (msg, type = 'info') => {
        setMessage(msg);
        setMessageType(type);
        setTimeout(() => setMessage(''), 3000);
    };

    const loadStats = async (email) => {
        try { setStats(await api.getStats(email)); } catch (_) {}
    };

    const doStartGame = async (email, code) => {
        const data = await api.startGame(email, code);
        setGameId(data.game_id);
        setWordLength(data.longueur);
        setTentatives([]);
        setCurrentGuess('');
        setGameOver(false);
        setPage('jeu');
    };

    // ── Handlers ───────────────────────────────────────────────────────────────
    const handleRegister = async (email, nom, prenom, password) => {
        setLoading(true);
        try {
            const u = await api.register(email, nom, prenom, password);
            localStorage.setItem('wordleUser', JSON.stringify(u));
            setUser(u);
            setPage('menu');
            showMessage(`Bienvenue ${u.prenom}!`, 'success');
        } catch (e) { showMessage(e.message, 'error'); }
        finally { setLoading(false); }
    };

    const handleLogin = async (email, password) => {
        setLoading(true);
        try {
            const u = await api.login(email, password);
            localStorage.setItem('wordleUser', JSON.stringify(u));
            setUser(u);
            await loadStats(u.email);
            setPage('menu');
            showMessage(`Bon retour ${u.prenom}!`, 'success');
        } catch (e) { showMessage(e.message, 'error'); }
        finally { setLoading(false); }
    };

    const handleLogout = () => {
        localStorage.removeItem('wordleUser');
        setUser(null);
        setLobby(null);
        setPage('home');
    };

    const handleCreateLobby = async (nom) => {
        setLoading(true);
        try {
            const data = await api.createLobby(nom, user.email);
            setLobby(data);
            setPage('lobby');
            showMessage(`Lobby créé ! Code : ${data.code}`, 'success');
        } catch (e) { showMessage(e.message, 'error'); }
        finally { setLoading(false); }
    };

    const handleJoinLobby = async (code) => {
        setLoading(true);
        try {
            const data = await api.joinLobby(code, user.email);
            setLobby(data);
            setPage('lobby');
            showMessage('Lobby rejoint !', 'success');
        } catch (e) { showMessage(e.message, 'error'); }
        finally { setLoading(false); }
    };

    const handleRefreshLobby = async () => {
        if (!lobby) return;
        try { setLobby(await api.getLobby(lobby.code)); } catch (_) {}
    };

    const handleStartGame = async () => {
        setLoading(true);
        try {
            await api.resetLobby(lobby.code); // remet started=false avant de lancer
            await doStartGame(user.email, lobby.code);
        }
        catch (e) { showMessage(e.message, 'error'); }
        finally { setLoading(false); }
    };

    const handleKeyPress = (lettre) => {
        if (gameOver || loading) return;
        if (lettre === 'ENTER') handleSubmitGuess();
        else if (lettre === 'BACK') setCurrentGuess((g) => g.slice(0, -1));
        else if (currentGuess.length < wordLength) setCurrentGuess((g) => g + lettre);
    };

    const handleSubmitGuess = async () => {
        if (currentGuess.length !== wordLength) {
            showMessage(`Le mot doit faire ${wordLength} lettres !`, 'error');
            return;
        }
        setLoading(true);
        try {
            const result = await api.submitGuess(gameId, currentGuess, user.email);
            const newT = { mot: currentGuess.toUpperCase(), correction: result.correction.map((c) => c.etat) };
            setTentatives((prev) => [...prev, newT]);
            setCurrentGuess('');

            if (result.gagne) {
                setGameOver(true);
                await loadStats(user.email);
                await handleRefreshLobby();
                showMessage(`Bravo ! Trouvé en ${tentatives.length + 1} essais ! +${result.score} pts`, 'success');
            } else if (result.perdu) {
                setGameOver(true);
                await loadStats(user.email);
                showMessage(`Perdu ! Le mot était : ${result.mot_secret}`, 'error');
            }
        } catch (e) { showMessage(e.message, 'error'); }
        finally { setLoading(false); }
    };

    const handleRetourLobby = async () => {
        await handleRefreshLobby();
        setPage('lobby');
    };

    // ── Rendu ──────────────────────────────────────────────────────────────────
    return (
        <div className="relative">
            {message && (
                <div className={`fixed top-4 left-1/2 transform -translate-x-1/2 px-6 py-3 rounded-lg shadow-lg z-50 font-semibold
                    ${messageType === 'success' ? 'bg-green-600 text-white' : ''}
                    ${messageType === 'error' ? 'bg-red-600 text-white' : ''}
                    ${messageType === 'info' ? 'bg-gray-800 text-white' : ''}`}>
                    {message}
                </div>
            )}

            {page === 'home'        && <HomePage onRegister={() => setPage('register')} onLogin={() => setPage('login')} />}
            {page === 'register'    && <RegisterPage onSubmit={handleRegister} onBack={() => setPage('home')} loading={loading} />}
            {page === 'login'       && <LoginPage onSubmit={handleLogin} onBack={() => setPage('home')} loading={loading} />}
            {page === 'menu'        && <MenuPage user={user} stats={stats} onCreateLobby={() => setPage('createLobby')} onJoinLobby={() => setPage('joinLobby')} onLogout={handleLogout} />}
            {page === 'createLobby' && <CreateLobbyPage onSubmit={handleCreateLobby} onBack={() => setPage('menu')} loading={loading} />}
            {page === 'joinLobby'   && <JoinLobbyPage onSubmit={handleJoinLobby} onBack={() => setPage('menu')} loading={loading} />}
            {page === 'lobby'       && <LobbyPage lobby={lobby} user={user} onStart={handleStartGame} onRefresh={handleRefreshLobby} onLeave={() => { setLobby(null); setPage('menu'); }} loading={loading} />}
            {page === 'jeu'         && <JeuPage tentatives={tentatives} currentGuess={currentGuess} wordLength={wordLength} gameOver={gameOver} lobby={lobby} user={user} loading={loading} onKeyPress={handleKeyPress} onRetourLobby={handleRetourLobby} />}
        </div>
    );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<WordleApp />);
