# NexCall AI — Guide de Déploiement

**Version** : 2.0.0
**Cible** : Serveur Linux (Ubuntu 22.04+) via FileZilla + SSH

---

## 1. Prérequis

### 1.1 Côté serveur

- Ubuntu 22.04+ ou Debian 12+
- Python 3.11+ installé
- Accès SSH (root ou sudo)
- Ports 80 et 443 ouverts dans le pare-feu
- Nom de domaine pointant vers le serveur (recommandé)

### 1.2 Côté client

- FileZilla (ou tout client SFTP)
- Un terminal SSH (PuTTY sur Windows, Terminal sur Mac/Linux)

### 1.3 Comptes requis

- Compte Ringover avec accès API (https://app.ringover.com/settings/api)
- Compte OpenAI avec crédit API (https://platform.openai.com/api-keys)

---

## 2. Transfert des fichiers

### 2.1 Avec FileZilla

1. Ouvrez FileZilla
2. Connectez-vous en SFTP :
   - Hôte : `sftp://votre-serveur.com`
   - Utilisateur : votre login SSH
   - Mot de passe : votre mot de passe SSH
   - Port : 22
3. Naviguez vers `/opt/` sur le serveur distant (panneau droit)
4. Transférez tout le dossier `nexcall-ai/` (panneau gauche → panneau droit)

**Fichiers à transférer** (tout le dossier) :
```
nexcall-ai/
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── app/            (tout le dossier)
├── data/           (dossier vide avec .gitkeep)
├── logs/           (dossier vide avec .gitkeep)
├── docs/           (documentation)
└── scripts/        (scripts de démarrage)
```

**Ne PAS transférer** :
- `.env` (sera créé sur le serveur)
- `venv/` (sera créé sur le serveur)
- `__pycache__/` (généré automatiquement)
- `*.db` (sera généré au premier lancement)

---

## 3. Installation sur le serveur

### 3.1 Connexion SSH

```bash
ssh utilisateur@votre-serveur.com
```

### 3.2 Installation des prérequis système

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx
```

### 3.3 Configuration du projet

```bash
cd /opt/nexcall-ai

# Créer l'environnement virtuel Python
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt

# Créer le fichier de configuration
cp .env.example .env
nano .env
```

### 3.4 Configuration du fichier .env

Modifiez les valeurs suivantes dans `.env` :

```ini
# OBLIGATOIRE : Désactiver le mode debug
DEBUG=false

# OBLIGATOIRE : Clé secrète unique (générer avec Python)
# python3 -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=votre_cle_secrete_generee_aleatoirement

# OBLIGATOIRE : Clés API
RINGOVER_API_KEY=votre_vraie_cle_ringover
OPENAI_API_KEY=sk-votre_vraie_cle_openai

# Numéros de téléphone
RINGOVER_PHONE_NUMBER=+33189701703
RINGOVER_TRANSFER_NUMBER=+33780989655

# Personnalisation de l'agent
AI_AGENT_NAME=Sophie
AI_COMPANY_NAME=VotreEntreprise
```

### 3.5 Vérification rapide

```bash
source venv/bin/activate
python3 -c "from app.config import settings; print(f'App: {settings.APP_NAME}, Ringover: {settings.is_ringover_configured}, OpenAI: {settings.is_openai_configured}')"
```

### 3.6 Premier test

```bash
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

Vérifiez dans le navigateur : `http://votre-serveur.com:8000`

Arrêtez avec `Ctrl+C`.

---

## 4. Configuration du service systemd

### 4.1 Créer le service

```bash
sudo nano /etc/systemd/system/nexcall-ai.service
```

Contenu :

```ini
[Unit]
Description=NexCall AI - Centre d'appels intelligent
After=network.target
Wants=network-online.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/nexcall-ai
Environment="PATH=/opt/nexcall-ai/venv/bin:/usr/bin"
ExecStart=/opt/nexcall-ai/venv/bin/gunicorn main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 4 \
    --bind 127.0.0.1:8000 \
    --access-logfile /opt/nexcall-ai/logs/access.log \
    --error-logfile /opt/nexcall-ai/logs/error.log \
    --timeout 120 \
    --graceful-timeout 30
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 4.2 Permissions

```bash
sudo chown -R www-data:www-data /opt/nexcall-ai
sudo chmod -R 755 /opt/nexcall-ai
sudo chmod 600 /opt/nexcall-ai/.env
```

### 4.3 Activer et démarrer

```bash
sudo systemctl daemon-reload
sudo systemctl enable nexcall-ai
sudo systemctl start nexcall-ai
sudo systemctl status nexcall-ai
```

### 4.4 Vérifier les logs

```bash
# Logs du service
sudo journalctl -u nexcall-ai -f

# Logs applicatifs
tail -f /opt/nexcall-ai/logs/error.log
tail -f /opt/nexcall-ai/logs/access.log
```

---

## 5. Configuration Nginx + HTTPS

### 5.1 Configuration Nginx

```bash
sudo nano /etc/nginx/sites-available/nexcall-ai
```

```nginx
server {
    listen 80;
    server_name nexcall.votre-domaine.com;

    # Redirection HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name nexcall.votre-domaine.com;

    # SSL sera configuré par Certbot (voir étape 5.2)

    # Taille max des uploads
    client_max_body_size 10M;

    # Timeouts pour les longues connexions IA
    proxy_read_timeout 120s;
    proxy_connect_timeout 10s;

    # Fichiers statiques (servis directement par Nginx)
    location /static/ {
        alias /opt/nexcall-ai/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy vers l'application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (pour futures évolutions)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Webhooks Ringover (accès direct sans cache)
    location /webhooks/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }
}
```

### 5.2 Activer le site et SSL

```bash
sudo ln -s /etc/nginx/sites-available/nexcall-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Certificat SSL Let's Encrypt (gratuit)
sudo certbot --nginx -d nexcall.votre-domaine.com
```

---

## 6. Configuration des Webhooks Ringover

### 6.1 Dans l'interface Ringover

1. Allez sur https://app.ringover.com
2. Paramètres → Webhooks
3. Ajoutez les URLs suivantes :

| Événement | URL |
|-----------|-----|
| Appel entrant | `https://nexcall.votre-domaine.com/webhooks/ringover/incoming` |
| Touche DTMF | `https://nexcall.votre-domaine.com/webhooks/ringover/dtmf` |
| Parole (STT) | `https://nexcall.votre-domaine.com/webhooks/ringover/speech` |
| Statut appel | `https://nexcall.votre-domaine.com/webhooks/ringover/status` |
| Fin d'appel | `https://nexcall.votre-domaine.com/webhooks/ringover/hangup` |

### 6.2 Vérification

Depuis le dashboard NexCall AI :
1. Allez dans Configuration
2. Cliquez sur "Tester la connexion" Ringover
3. Vérifiez que le statut passe à "Connecté"

---

## 7. Test de bout en bout

### 7.1 Via le simulateur (sans téléphone)

1. Ouvrez `https://nexcall.votre-domaine.com`
2. Cliquez sur "Simuler un appel"
3. Lancez la simulation
4. Vérifiez :
   - La réponse IA est cohérente
   - Un lead est créé dans l'onglet Leads
   - L'appel apparaît dans l'onglet Appels

### 7.2 Via un vrai appel

1. Appelez le numéro Ringover configuré
2. Écoutez le message IVR
3. Appuyez sur 1 ou 2
4. Dialoguez avec l'agent IA
5. Vérifiez dans le dashboard :
   - L'appel en temps réel
   - Le lead créé avec score
   - Le résumé IA après raccrochage

---

## 8. Maintenance courante

### 8.1 Commandes utiles

```bash
# Statut du service
sudo systemctl status nexcall-ai

# Redémarrer
sudo systemctl restart nexcall-ai

# Arrêter
sudo systemctl stop nexcall-ai

# Voir les logs en direct
sudo journalctl -u nexcall-ai -f

# Backup de la base de données
cp /opt/nexcall-ai/data/nexcall.db /opt/nexcall-ai/data/backup_$(date +%Y%m%d).db
```

### 8.2 Mise à jour de l'application

```bash
# 1. Transférer les nouveaux fichiers via FileZilla
# 2. Sur le serveur :
cd /opt/nexcall-ai
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart nexcall-ai
```

### 8.3 Rotation des logs

Créez `/etc/logrotate.d/nexcall-ai` :

```
/opt/nexcall-ai/logs/*.log {
    weekly
    rotate 12
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload nexcall-ai
    endscript
}
```

---

## 9. Dépannage

| Problème | Solution |
|----------|----------|
| Le service ne démarre pas | `sudo journalctl -u nexcall-ai -n 50` pour voir les erreurs |
| Erreur "Permission denied" | `sudo chown -R www-data:www-data /opt/nexcall-ai` |
| Ringover non connecté | Vérifier la clé API dans .env et redémarrer |
| OpenAI ne répond pas | Vérifier la clé API et le crédit sur platform.openai.com |
| 502 Bad Gateway (Nginx) | Le service FastAPI est arrêté : `sudo systemctl start nexcall-ai` |
| Webhooks non reçus | Vérifier les URLs dans Ringover + certificat SSL valide |
| Base de données corrompue | Restaurer le dernier backup depuis data/ |
