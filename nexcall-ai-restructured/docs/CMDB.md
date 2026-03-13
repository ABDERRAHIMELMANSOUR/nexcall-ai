# NexCall AI — CMDB (Configuration Management Database)

**Version** : 2.0.0
**Dernière mise à jour** : Mars 2026

---

## 1. Composants logiciels

### 1.1 Application

| Composant | Rôle | Technologie | Version | Fichier(s) |
|-----------|------|-------------|---------|------------|
| FastAPI App | Serveur web ASGI | FastAPI | 0.111.0 | `main.py` |
| Config | Configuration centralisée | pydantic-settings | 2.2.1 | `app/config.py` |
| Database | ORM async | SQLAlchemy | 2.0.30 | `app/database.py` |
| AI Agent | Cerveau IA conversationnel | OpenAI SDK | 1.30.1 | `app/services/ai_agent.py` |
| IVR Service | Menu vocal interactif | Python natif | — | `app/services/ivr_service.py` |
| Lead Service | Qualification prospects | Python natif | — | `app/services/lead_service.py` |
| Ringover Client | Client API téléphonie | httpx | 0.27.0 | `app/services/ringover_service.py` |
| Templates | Interface utilisateur | Jinja2 | 3.1.4 | `app/templates/*.html` |
| Static CSS | Design system | CSS3 | — | `app/static/css/style.css` |

### 1.2 Modèles de données

| Modèle | Table BDD | Champs principaux | Fichier |
|--------|-----------|-------------------|---------|
| Call | `calls` | id, ringover_call_id, caller_number, status, transcript, ai_summary | `app/models/call.py` |
| Lead | `leads` | id, phone, first_name, last_name, score, status, interest | `app/models/lead.py` |
| Campaign | `campaigns` | id, name, status, type, ai_system_prompt, total_calls | `app/models/campaign.py` |
| Configuration | `configurations` | id, key, value, category, is_secret | `app/models/configuration.py` |

### 1.3 Routeurs API

| Routeur | Préfixe | Nombre d'endpoints | Fichier |
|---------|---------|:-----------------:|---------|
| Pages | `/` | 5 | `app/routers/pages.py` |
| Calls | `/api/calls` | 6 | `app/routers/calls.py` |
| Leads | `/api/leads` | 7 | `app/routers/leads.py` |
| Campaigns | `/api/campaigns` | 8 | `app/routers/campaigns.py` |
| Configuration | `/api/config` | 5 | `app/routers/configuration.py` |
| Webhooks | `/webhooks/ringover` | 5 | `app/routers/webhooks.py` |

---

## 2. Dépendances

### 2.1 Dépendances Python (runtime)

| Package | Version | Rôle | Critique |
|---------|---------|------|:--------:|
| fastapi | 0.111.0 | Framework web ASGI | ✓ |
| uvicorn[standard] | 0.29.0 | Serveur ASGI | ✓ |
| gunicorn | 22.0.0 | Process manager production | ✓ |
| sqlalchemy | 2.0.30 | ORM base de données | ✓ |
| aiosqlite | 0.20.0 | Driver SQLite async | ✓ (dev) |
| alembic | 1.13.1 | Migrations BDD | — |
| python-dotenv | 1.0.1 | Variables d'environnement | ✓ |
| pydantic | 2.7.1 | Validation de données | ✓ |
| pydantic-settings | 2.2.1 | Configuration typée | ✓ |
| httpx | 0.27.0 | Client HTTP async | ✓ |
| openai | 1.30.1 | SDK OpenAI | ✓ |
| jinja2 | 3.1.4 | Moteur de templates | ✓ |
| python-multipart | 0.0.9 | Upload de fichiers | — |
| aiofiles | 23.2.1 | Fichiers async | — |
| websockets | 12.0 | Support WebSocket | — |
| passlib[bcrypt] | 1.7.4 | Hachage de mots de passe | — |
| python-jose[cryptography] | 3.3.0 | Tokens JWT | — |

### 2.2 Dépendances système

| Composant | Version minimale | Rôle |
|-----------|:---------------:|------|
| Python | 3.11+ | Runtime |
| pip | 23+ | Gestionnaire de paquets |
| Linux (Ubuntu) | 22.04+ | Système d'exploitation serveur |
| Nginx | 1.18+ | Reverse proxy HTTPS (production) |

### 2.3 Services externes

| Service | Fournisseur | URL API | Protocole | Obligatoire |
|---------|-------------|---------|-----------|:-----------:|
| Téléphonie | Ringover | `https://public-api.ringover.com/v2` | REST HTTPS | ✓ |
| IA Chat | OpenAI | `https://api.openai.com/v1/chat/completions` | REST HTTPS | ✓ |
| IA TTS | OpenAI | `https://api.openai.com/v1/audio/speech` | REST HTTPS | — |
| IA STT | OpenAI | `https://api.openai.com/v1/audio/transcriptions` | REST HTTPS | — |

---

## 3. Configuration

### 3.1 Variables d'environnement

| Variable | Catégorie | Type | Valeur par défaut | Sensible |
|----------|-----------|------|:-----------------:|:--------:|
| APP_NAME | Application | string | "NexCall AI" | — |
| APP_HOST | Application | string | "0.0.0.0" | — |
| APP_PORT | Application | int | 8000 | — |
| DEBUG | Application | bool | false | — |
| SECRET_KEY | Application | string | — | ✓ |
| DATABASE_URL | BDD | string | sqlite+aiosqlite:///./data/nexcall.db | — |
| RINGOVER_API_KEY | Ringover | string | — | ✓ |
| RINGOVER_API_URL | Ringover | string | https://public-api.ringover.com/v2 | — |
| RINGOVER_WEBHOOK_SECRET | Ringover | string | — | ✓ |
| RINGOVER_PHONE_NUMBER | Ringover | string | — | — |
| RINGOVER_TRANSFER_NUMBER | Ringover | string | — | — |
| OPENAI_API_KEY | OpenAI | string | — | ✓ |
| OPENAI_MODEL | OpenAI | string | gpt-4o | — |
| OPENAI_TTS_MODEL | OpenAI | string | tts-1 | — |
| OPENAI_TTS_VOICE | OpenAI | string | nova | — |
| OPENAI_STT_MODEL | OpenAI | string | whisper-1 | — |
| OPENAI_MAX_TOKENS | OpenAI | int | 600 | — |
| AI_AGENT_NAME | Agent IA | string | Sophie | — |
| AI_COMPANY_NAME | Agent IA | string | AssurancePro | — |
| AI_LANGUAGE | Agent IA | string | fr | — |
| AI_TEMPERATURE | Agent IA | float | 0.7 | — |
| IVR_GREETING | IVR | string | (message d'accueil) | — |
| LEAD_SCORE_THRESHOLD | Leads | int | 70 | — |

### 3.2 Ports réseau

| Port | Service | Protocole | Direction |
|:----:|---------|-----------|:---------:|
| 8000 | FastAPI / Gunicorn | HTTP | Inbound |
| 80 | Nginx (HTTP) | HTTP | Inbound |
| 443 | Nginx (HTTPS) | HTTPS | Inbound |
| 443 | OpenAI API | HTTPS | Outbound |
| 443 | Ringover API | HTTPS | Outbound |

### 3.3 Fichiers de configuration

| Fichier | Emplacement | Rôle |
|---------|-------------|------|
| .env | Racine projet | Variables d'environnement |
| .env.example | Racine projet | Template de configuration |
| requirements.txt | Racine projet | Dépendances Python |
| start.sh | scripts/ | Script de démarrage production |

---

## 4. Infrastructure

### 4.1 Architecture de déploiement (production)

```
Internet
    │
    ▼
┌──────────────┐
│   Nginx      │  Port 80/443 (HTTPS + reverse proxy)
│   + SSL      │
└──────┬───────┘
       │ proxy_pass :8000
┌──────▼───────┐
│  Gunicorn    │  4 workers Uvicorn
│  + Uvicorn   │  Port 8000 (localhost)
└──────┬───────┘
       │
┌──────▼───────┐
│  FastAPI     │  Application NexCall AI
│  Application │
└──────┬───────┘
       │
┌──────▼───────┐
│   SQLite /   │  Base de données
│  PostgreSQL  │  data/nexcall.db
└──────────────┘
```

### 4.2 Dimensionnement recommandé

| Ressource | Minimum | Recommandé |
|-----------|:-------:|:----------:|
| vCPU | 1 | 2 |
| RAM | 1 Go | 2 Go |
| Stockage | 5 Go | 20 Go |
| Bande passante | 10 Mbps | 50 Mbps |

### 4.3 Sauvegardes

| Élément | Fréquence | Méthode |
|---------|-----------|---------|
| Base de données SQLite | Quotidienne | Copie du fichier `data/nexcall.db` |
| Fichier .env | Après chaque modification | Copie manuelle sécurisée |
| Logs | Rotation hebdomadaire | logrotate ou script cron |

---

## 5. Monitoring et maintenance

### 5.1 Endpoints de monitoring

| Endpoint | Méthode | Rôle |
|----------|---------|------|
| `/health` | GET | Health check (status, version, intégrations) |
| `/api/config/status` | GET | Statut détaillé Ringover + OpenAI |
| `/docs` | GET | Documentation API interactive (Swagger) |

### 5.2 Logs

| Fichier | Contenu | Rotation |
|---------|---------|----------|
| `logs/access.log` | Requêtes HTTP entrantes | Hebdomadaire |
| `logs/error.log` | Erreurs serveur | Hebdomadaire |
| stdout | Logs applicatifs (nexcall) | — |

### 5.3 Procédures de maintenance

| Action | Commande | Fréquence |
|--------|----------|-----------|
| Mise à jour dépendances | `pip install -r requirements.txt --upgrade` | Mensuelle |
| Redémarrage | `sudo systemctl restart nexcall-ai` | Après mise à jour |
| Vérification santé | `curl http://localhost:8000/health` | Continue (monitoring) |
| Backup BDD | `cp data/nexcall.db data/nexcall_backup_$(date +%Y%m%d).db` | Quotidienne |
