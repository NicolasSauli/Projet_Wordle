// ── View : composants React purs (présentation uniquement) ────────────────────

const HomePage = ({ onRegister, onLogin }) => (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-purple-700 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
            <div className="text-center mb-8">
                <h1 className="text-5xl font-bold text-gray-800 mb-2">WORDLE</h1>
                <p className="text-gray-600">Multijoueur</p>
            </div>
            <div className="space-y-4">
                <button onClick={onRegister} className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition">
                    S'inscrire
                </button>
                <button onClick={onLogin} className="w-full bg-gray-600 hover:bg-gray-700 text-white font-semibold py-3 px-6 rounded-lg transition">
                    Se connecter
                </button>
            </div>
        </div>
    </div>
);

const RegisterPage = ({ onSubmit, onBack, loading }) => {
    const [form, setForm] = React.useState({ email: '', nom: '', prenom: '', password: '' });
    const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });
    const valid = form.email && form.nom && form.prenom && form.password;

    return (
        <div className="min-h-screen bg-gradient-to-br from-green-600 to-teal-700 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
                <h2 className="text-3xl font-bold text-gray-800 mb-6">Inscription</h2>
                <div className="space-y-4">
                    {['email', 'nom', 'prenom'].map((k) => (
                        <input key={k} type={k === 'email' ? 'email' : 'text'} placeholder={k.charAt(0).toUpperCase() + k.slice(1)}
                            value={form[k]} onChange={set(k)}
                            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-green-500 focus:outline-none" />
                    ))}
                    <input type="password" placeholder="Mot de passe" value={form.password} onChange={set('password')}
                        className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-green-500 focus:outline-none" />
                    <button onClick={() => valid && onSubmit(form.email, form.nom, form.prenom, form.password)}
                        disabled={loading || !valid}
                        className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-semibold py-3 rounded-lg transition">
                        {loading ? 'Chargement...' : 'Créer mon compte'}
                    </button>
                </div>
                <button onClick={onBack} className="w-full mt-4 text-gray-600 hover:text-gray-800">Retour</button>
            </div>
        </div>
    );
};

const LoginPage = ({ onSubmit, onBack, loading }) => {
    const [form, setForm] = React.useState({ email: '', password: '' });
    const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });
    const valid = form.email && form.password;

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
                <h2 className="text-3xl font-bold text-gray-800 mb-6">Connexion</h2>
                <div className="space-y-4">
                    <input type="email" placeholder="Email" value={form.email} onChange={set('email')}
                        className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none" />
                    <input type="password" placeholder="Mot de passe" value={form.password} onChange={set('password')}
                        onKeyPress={(e) => e.key === 'Enter' && valid && onSubmit(form.email, form.password)}
                        className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none" />
                    <button onClick={() => valid && onSubmit(form.email, form.password)}
                        disabled={loading || !valid}
                        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 rounded-lg transition">
                        {loading ? 'Chargement...' : 'Se connecter'}
                    </button>
                </div>
                <button onClick={onBack} className="w-full mt-4 text-gray-600 hover:text-gray-800">Retour</button>
            </div>
        </div>
    );
};

const MenuPage = ({ user, stats, onCreateLobby, onJoinLobby, onLogout }) => (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 to-pink-700 p-4">
        <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-2xl shadow-2xl p-8 mb-6">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h2 className="text-3xl font-bold text-gray-800">Bienvenue {user.prenom}!</h2>
                        <p className="text-gray-600">{user.email}</p>
                    </div>
                    <button onClick={onLogout} className="text-red-600 hover:text-red-800 font-semibold">Déconnexion</button>
                </div>
                <div className="grid grid-cols-3 gap-4">
                    {[['🏆', stats.victoires, 'Victoires'], ['🎮', stats.parties, 'Parties'], ['⭐', stats.meilleurScore, 'Meilleur Score']].map(([icon, val, label]) => (
                        <div key={label} className="bg-blue-100 p-4 rounded-lg text-center">
                            <div className="text-3xl mb-2">{icon}</div>
                            <div className="text-2xl font-bold text-gray-800">{val}</div>
                            <div className="text-sm text-gray-600">{label}</div>
                        </div>
                    ))}
                </div>
            </div>
            <div className="grid md:grid-cols-2 gap-6">
                <button onClick={onCreateLobby} className="bg-white hover:bg-gray-50 rounded-2xl shadow-lg p-8 text-center transition">
                    <div className="text-5xl mb-4">👥</div>
                    <h3 className="text-2xl font-bold text-gray-800 mb-2">Créer un Lobby</h3>
                    <p className="text-gray-600">Invitez vos amis à jouer</p>
                </button>
                <button onClick={onJoinLobby} className="bg-white hover:bg-gray-50 rounded-2xl shadow-lg p-8 text-center transition">
                    <div className="text-5xl mb-4">🚀</div>
                    <h3 className="text-2xl font-bold text-gray-800 mb-2">Rejoindre un Lobby</h3>
                    <p className="text-gray-600">Entrez un code de lobby</p>
                </button>
            </div>
        </div>
    </div>
);

const CreateLobbyPage = ({ onSubmit, onBack, loading }) => {
    const [nom, setNom] = React.useState('');
    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-600 to-blue-700 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
                <h2 className="text-3xl font-bold text-gray-800 mb-6">Créer un Lobby</h2>
                <input type="text" placeholder="Nom du lobby" value={nom} onChange={(e) => setNom(e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-indigo-500 focus:outline-none mb-4" />
                <button onClick={() => nom && onSubmit(nom)} disabled={loading || !nom}
                    className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-semibold py-3 rounded-lg transition mb-4">
                    {loading ? 'Chargement...' : 'Créer'}
                </button>
                <button onClick={onBack} className="w-full text-gray-600 hover:text-gray-800">Retour</button>
            </div>
        </div>
    );
};

const JoinLobbyPage = ({ onSubmit, onBack, loading }) => {
    const [code, setCode] = React.useState('');
    return (
        <div className="min-h-screen bg-gradient-to-br from-teal-600 to-green-700 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
                <h2 className="text-3xl font-bold text-gray-800 mb-6">Rejoindre un Lobby</h2>
                <input type="text" placeholder="Code du lobby (6 chiffres)" value={code}
                    onChange={(e) => setCode(e.target.value)} maxLength={6}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-teal-500 focus:outline-none mb-4 text-center text-2xl tracking-widest" />
                <button onClick={() => code.length === 6 && onSubmit(code)} disabled={loading || code.length !== 6}
                    className="w-full bg-teal-600 hover:bg-teal-700 disabled:bg-gray-400 text-white font-semibold py-3 rounded-lg transition mb-4">
                    {loading ? 'Chargement...' : 'Rejoindre'}
                </button>
                <button onClick={onBack} className="w-full text-gray-600 hover:text-gray-800">Retour</button>
            </div>
        </div>
    );
};

const LobbyPage = ({ lobby, user, onStart, onRefresh, onLeave, loading }) => (
    <div className="min-h-screen bg-gradient-to-br from-orange-600 to-red-700 p-4">
        <div className="max-w-2xl mx-auto">
            <div className="bg-white rounded-2xl shadow-2xl p-8">
                <div className="mb-6">
                    <h2 className="text-3xl font-bold text-gray-800 mb-2">{lobby.nom}</h2>
                    <div className="text-xl font-mono bg-gray-100 p-3 rounded-lg text-center">
                        Code: <span className="font-bold text-orange-600">{lobby.code}</span>
                    </div>
                </div>

                <div className="mb-6">
                    <div className="flex justify-between items-center mb-3">
                        <h3 className="text-xl font-bold text-gray-700">Joueurs ({lobby.joueurs.length})</h3>
                        <button onClick={onRefresh} className="text-orange-600 hover:text-orange-800 text-sm">Actualiser</button>
                    </div>
                    <div className="space-y-2">
                        {lobby.joueurs.map((j, i) => (
                            <div key={i} className="bg-gray-50 p-3 rounded-lg flex justify-between items-center">
                                <span className="font-semibold">
                                    {j.nom}
                                    {j.email === lobby.createur && <span className="text-xs text-orange-600 ml-2">(Hôte)</span>}
                                </span>
                                <span className="text-orange-600 font-bold">{j.score} pts</span>
                            </div>
                        ))}
                    </div>
                </div>

                {user.email === lobby.createur ? (
                    <button onClick={onStart} disabled={loading}
                        className="w-full bg-orange-600 hover:bg-orange-700 disabled:bg-gray-400 text-white font-semibold py-3 rounded-lg transition mb-4">
                        {loading ? 'Chargement...' : 'Démarrer la partie'}
                    </button>
                ) : (
                    <div className="w-full bg-gray-100 text-gray-500 py-3 text-center rounded-lg mb-4 animate-pulse">
                        En attente que l'hôte démarre...
                    </div>
                )}

                <button onClick={onLeave} className="w-full text-gray-600 hover:text-gray-800">Quitter le lobby</button>
            </div>
        </div>
    </div>
);

const JeuPage = ({ tentatives, currentGuess, wordLength, gameOver, lobby, user, loading, onKeyPress, onRetourLobby }) => {
    const CLAVIER = [
        ['A', 'Z', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['Q', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M'],
        ['ENTER', 'W', 'X', 'C', 'V', 'B', 'N', 'BACK'],
    ];

    const letterStatus = React.useMemo(() => {
        const s = {};
        tentatives.forEach((t) => {
            t.mot.split('').forEach((lettre, i) => {
                const etat = t.correction[i];
                if (etat === 'correct') s[lettre] = 'correct';
                else if (etat === 'present' && s[lettre] !== 'correct') s[lettre] = 'present';
                else if (etat === 'absent' && !s[lettre]) s[lettre] = 'absent';
            });
        });
        return s;
    }, [tentatives]);

    const keyColor = (l) => {
        if (l === 'ENTER' || l === 'BACK') return 'bg-gray-400 hover:bg-gray-500';
        const s = letterStatus[l];
        if (s === 'correct') return 'bg-green-500 text-white';
        if (s === 'present') return 'bg-yellow-500 text-white';
        if (s === 'absent') return 'bg-gray-600 text-white';
        return 'bg-gray-300 hover:bg-gray-400';
    };

    const cellColor = (etat) => {
        if (etat === 'correct') return 'bg-green-500 text-white border-green-500';
        if (etat === 'present') return 'bg-yellow-500 text-white border-yellow-500';
        if (etat === 'absent') return 'bg-gray-400 text-white border-gray-400';
        return '';
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-700 to-slate-900 p-4">
            <div className="max-w-lg mx-auto">
                {/* Grille */}
                <div className="bg-white rounded-2xl shadow-2xl p-6 mb-4">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-2xl font-bold text-gray-800">WORDLE</h2>
                        <div className="text-sm text-gray-600">Essai {Math.min(tentatives.length + 1, 6)}/6</div>
                    </div>

                    <div className="space-y-2 mb-6">
                        {[...Array(6)].map((_, row) => (
                            <div key={row} className="flex gap-2 justify-center">
                                {[...Array(wordLength)].map((_, col) => {
                                    const t = tentatives[row];
                                    const isCurrent = row === tentatives.length;
                                    const lettre = t ? t.mot[col] : (isCurrent ? currentGuess[col] : '') || '';
                                    const etat = t ? t.correction[col] : '';
                                    return (
                                        <div key={col} className={`w-14 h-14 border-2 rounded flex items-center justify-center text-2xl font-bold transition-all
                                            ${cellColor(etat)} ${!etat && lettre ? 'border-gray-400 pop' : 'border-gray-300'}`}>
                                            {lettre}
                                        </div>
                                    );
                                })}
                            </div>
                        ))}
                    </div>

                    {gameOver && (
                        <div className="mb-4 p-4 bg-blue-100 rounded-lg text-center">
                            <button onClick={onRetourLobby}
                                className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg">
                                Retour au lobby
                            </button>
                        </div>
                    )}
                </div>

                {/* Scores */}
                {lobby && (
                    <div className="bg-white rounded-2xl shadow-2xl p-4 mb-4">
                        <h3 className="text-xs font-bold text-gray-500 uppercase mb-2">Scores</h3>
                        <div className="space-y-1">
                            {lobby.joueurs.map((j, i) => (
                                <div key={i} className="flex justify-between text-sm">
                                    <span className={j.email === user.email ? 'font-bold text-gray-800' : 'text-gray-600'}>{j.nom}</span>
                                    <span className="text-orange-600 font-bold">{j.score} pts</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Clavier */}
                <div className="bg-white rounded-2xl shadow-2xl p-4">
                    <div className="space-y-2">
                        {CLAVIER.map((row, i) => (
                            <div key={i} className="flex gap-1 justify-center">
                                {row.map((l) => (
                                    <button key={l} onClick={() => onKeyPress(l)} disabled={gameOver || loading}
                                        className={`${l === 'ENTER' || l === 'BACK' ? 'px-3 text-xs' : 'w-9'} h-12 font-semibold rounded transition ${keyColor(l)} disabled:opacity-50 disabled:cursor-not-allowed`}>
                                        {l === 'BACK' ? '⌫' : l}
                                    </button>
                                ))}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};
