# NexCall AI v2.0

**Plateforme de centre d'appels intelligent** intégrant **Ringover** pour la téléphonie et **OpenAI** pour les conversations IA.

---

## Fonctionnalités

- **Agent IA conversationnel** — GPT-4o répond aux appels entrants, qualifie les prospects et extrait automatiquement les données des leads
- **IVR intelligent** — Menu vocal interactif avec routage automatique (Assurance Auto, Santé, Transfert agent)
- **Qualification de leads** — Scoring automatique 0–100, catégorisation (chaud/tiède/qualifié/froid), suivi en temps réel
- **Gestion de campagnes** — Création, activation, pause et suivi de campagnes d'appels avec métriques détaillées
- **Webhooks Ringover** — Intégration temps réel : appel entrant, DTMF, reconnaissance vocale, statut, fin d'appel
- **Dashboard en temps réel** — Vue d'ensemble complète avec statistiques, appels récents et leads prioritaires
- **Simulateur d'appels** — Test de l'agent IA sans téléphonie réelle

---

## Architecture technique

```
nexcall-ai/
├── main.py                    # Point d'entrée FastAPI
├── requirements.txt           # Dépendances Python
├── .env.example               # Template de configuration
├── .gitignore
│
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuration centralisée (pydantic-settings)
│   ├── database.py            # SQLAlchemy async (SQLite/PostgreSQL)
│   │
│   ├── models/                # Modèles de données
│   │   ├── call.py            # Modèle Call (appels)
│   │   ├── lead.py            # Modèle Lead (prospects)
│   │   ├── campaign.py        # Modèle Campaign (campagnes)
│   │   └── configuration.py   # Modèle Configuration (paramètres)
│   │
│   ├── routers/               # Routes API
│   │   ├── pages.py           # Pages HTML (dashboard, appels, leads...)
│   │   ├── calls.py           # API CRUD appels + simulation
│   │   ├── leads.py           # API CRUD leads
│   │   ├── campaigns.py       # API CRUD campagnes
│   │   ├── configuration.py   # API configuration système
│   │   └── webhooks.py        # Webhooks Ringover
│   │
│   ├── services/              # Logique métier
│   │   ├── ai_agent.py        # Agent IA (OpenAI GPT + TTS + STT)
│   │   ├── ivr_service.py     # Service IVR (menu vocal)
│   │   ├── lead_service.py    # Service leads (qualification)
│   │   └── ringover_service.py # Client API Ringover
│   │
│   ├── templates/             # Templates Jinja2
│   │   ├── base.html          # Layout principal
│   │   ├── dashboard.html
│   │   ├── calls.html
│   │   ├── leads.html
│   │   ├── campaigns.html
│   │   └── configuration.html
│   │
│   ├── static/                # Fichiers statiques
│   │   └── css/style.css      # Feuille de style principale
│   │
│   └── utils/                 # Utilitaires
│       └── __init__.py
│
├── data/                      # Base de données SQLite
├── logs/                      # Fichiers de log
├── docs/                      # Documentation
└── scripts/
    └── start.sh               # Script de démarrage production
```

---

## Installation

### Prérequis

- Python 3.11+
- pip

### Installation locale (développement)

```bash
# 1. Cloner le projet
git clone <repo-url> nexcall-ai
cd nexcall-ai

# 2. Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OU
venv\Scripts\activate     # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer l'environnement
cp .env.example .env
# Éditez .env avec vos clés API

# 5. Lancer le serveur
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Accès

- **Dashboard** : http://127.0.0.1:8000
- **API docs (Swagger)** : http://127.0.0.1:8000/docs
- **API docs (ReDoc)** : http://127.0.0.1:8000/redoc

---

## Configuration

Toutes les variables sont dans le fichier `.env`. Les essentielles :

| Variable | Description | Obligatoire |
|----------|-------------|:-----------:|
| `RINGOVER_API_KEY` | Clé API Ringover | ✓ |
| `OPENAI_API_KEY` | Clé API OpenAI | ✓ |
| `RINGOVER_PHONE_NUMBER` | Numéro de réception | ✓ |
| `RINGOVER_TRANSFER_NUMBER` | Numéro de transfert agent | ✓ |
| `SECRET_KEY` | Clé secrète de l'application | ✓ |
| `AI_AGENT_NAME` | Nom de l'agent IA | — |
| `AI_COMPANY_NAME` | Nom de l'entreprise | — |

---

## Webhooks Ringover

Configurez ces URLs dans **Ringover → Paramètres → Webhooks** :

| Événement | URL |
|-----------|-----|
| Appel entrant | `https://votre-domaine.com/webhooks/ringover/incoming` |
| Touche DTMF | `https://votre-domaine.com/webhooks/ringover/dtmf` |
| Parole client | `https://votre-domaine.com/webhooks/ringover/speech` |
| Statut appel | `https://votre-domaine.com/webhooks/ringover/status` |
| Fin d'appel | `https://votre-domaine.com/webhooks/ringover/hangup` |

**Pour tester localement**, utilisez ngrok :
```bash
ngrok http 8000
```

---

## Déploiement en production

### Via FileZilla (hébergement classique)

1. **Transférez** tout le dossier `nexcall-ai/` sur votre serveur via FTP/SFTP
2. **Connectez-vous** en SSH au serveur
3. **Exécutez** :

```bash
cd /chemin/vers/nexcall-ai

# Créer et activer l'env virtuel
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurer
cp .env.example .env
nano .env  # Remplir les clés API

# Lancer en production
chmod +x scripts/start.sh
./scripts/start.sh
```

### Avec systemd (recommandé)

Créez `/etc/systemd/system/nexcall-ai.service` :

```ini
[Unit]
Description=NexCall AI
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/nexcall-ai
ExecStart=/opt/nexcall-ai/venv/bin/gunicorn main:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable nexcall-ai
sudo systemctl start nexcall-ai
```

### Avec Nginx (reverse proxy)

```nginx
server {
    listen 80;
    server_name nexcall.votre-domaine.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## API Endpoints

### Appels
- `GET /api/calls` — Liste des appels
- `GET /api/calls/stats` — Statistiques
- `GET /api/calls/{id}` — Détail d'un appel
- `POST /api/calls/simulate` — Simulation d'appel
- `POST /api/calls/{id}/transfer` — Transfert
- `DELETE /api/calls/{id}` — Suppression

### Leads
- `GET /api/leads` — Liste des leads
- `GET /api/leads/stats` — Statistiques
- `POST /api/leads` — Création
- `PUT /api/leads/{id}` — Modification
- `DELETE /api/leads/{id}` — Suppression

### Campagnes
- `GET /api/campaigns` — Liste
- `POST /api/campaigns` — Création
- `PUT /api/campaigns/{id}` — Modification
- `POST /api/campaigns/{id}/activate` — Activation
- `POST /api/campaigns/{id}/pause` — Pause
- `DELETE /api/campaigns/{id}` — Suppression

### Configuration
- `GET /api/config` — Configuration actuelle
- `POST /api/config` — Sauvegarde
- `GET /api/config/status` — Statut des intégrations
- `POST /api/config/test-ringover` — Test connexion Ringover

### Webhooks
- `POST /webhooks/ringover/incoming` — Appel entrant
- `POST /webhooks/ringover/dtmf` — Touche DTMF
- `POST /webhooks/ringover/speech` — Parole transcrite
- `POST /webhooks/ringover/status` — Changement de statut
- `POST /webhooks/ringover/hangup` — Fin d'appel

---

## Licence

Propriétaire — Usage interne uniquement.
