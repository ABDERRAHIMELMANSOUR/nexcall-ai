# NexCall AI — Cahier des Charges

**Version** : 2.0.0
**Date** : Mars 2026
**Statut** : Production

---

## 1. Description fonctionnelle

### 1.1 Présentation

NexCall AI est une plateforme de centre d'appels intelligent qui automatise la réception, la qualification et le routage des appels entrants. Elle combine la téléphonie Ringover avec l'intelligence artificielle OpenAI pour offrir une expérience conversationnelle naturelle aux appelants, tout en qualifiant automatiquement les prospects.

### 1.2 Objectifs métier

- Automatiser l'accueil et la qualification des appels entrants
- Réduire le temps de traitement par appel de 60%
- Qualifier automatiquement les prospects avec un scoring 0–100
- Transférer uniquement les leads qualifiés (score ≥ 70) vers les agents humains
- Fournir un dashboard temps réel pour le suivi d'activité
- Permettre la gestion de campagnes d'appels multiples

### 1.3 Fonctionnalités principales

**F1 — IVR (Interactive Voice Response)**
- Menu vocal d'accueil configurable
- Détection des touches DTMF (1 = Auto, 2 = Santé, 3 = Agent)
- Routage intelligent selon le choix

**F2 — Agent IA conversationnel**
- Conversation naturelle en français via GPT-4o
- Personnalité configurable (nom, entreprise, ton)
- Collecte progressive des informations : prénom, nom, besoin, budget, urgence
- Extraction automatique des données lead via balises structurées <LEAD_DATA>
- Résumé automatique post-appel

**F3 — Qualification de leads**
- Scoring automatique 0–100 basé sur l'intérêt, le budget et l'urgence
- Catégorisation : Chaud (≥80), Tiède (≥60), Qualifié (≥30), Froid (<30)
- Fusion intelligente des données lors d'appels multiples du même numéro
- Le score ne descend jamais pendant un même appel

**F4 — Gestion des campagnes**
- Création de campagnes avec script IA et message IVR personnalisés
- Cycle de vie : Brouillon → Active → Pause → Terminée
- Métriques automatiques : appels, taux de réponse, leads générés, transferts

**F5 — Dashboard temps réel**
- Statistiques globales (appels, leads, scores, durées)
- Liste des appels récents avec statuts
- Leads prioritaires triés par score
- Auto-rafraîchissement toutes les 30 secondes

**F6 — Simulateur d'appels**
- Test complet du pipeline sans téléphonie réelle
- Validation de la configuration OpenAI
- Création effective d'un appel et d'un lead en base

**F7 — Configuration dynamique**
- Interface web pour les clés API, paramètres agent et IVR
- Test de connexion Ringover intégré
- Affichage des URLs webhooks à configurer

---

## 2. Architecture technique

### 2.1 Stack technologique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Backend | Python + FastAPI | 3.11+ / 0.111 |
| ORM | SQLAlchemy (async) | 2.0.30 |
| Base de données | SQLite (dev) / PostgreSQL (prod) | — |
| IA | OpenAI GPT-4o + TTS + STT | API v1 |
| Téléphonie | Ringover API v2 | REST |
| Frontend | HTML5 + CSS3 + JavaScript vanilla | — |
| Templates | Jinja2 | 3.1.4 |
| HTTP Client | httpx (async) | 0.27.0 |
| Serveur prod | Gunicorn + Uvicorn workers | — |

### 2.2 Architecture applicative

```
┌─────────────────────────────────────────────────────┐
│                    CLIENT (Navigateur)                │
│              Dashboard / Pages HTML / API             │
└───────────────────────┬─────────────────────────────┘
                        │ HTTP/HTTPS
┌───────────────────────▼─────────────────────────────┐
│                   FASTAPI SERVER                      │
│                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │  Pages   │  │   API    │  │    Webhooks      │   │
│  │ Router   │  │ Routers  │  │    Ringover      │   │
│  └──────────┘  └──────────┘  └──────────────────┘   │
│                        │                              │
│  ┌─────────────────────▼────────────────────────┐    │
│  │              SERVICES LAYER                   │    │
│  │                                               │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐   │    │
│  │  │ AI Agent │  │ IVR Svc  │  │ Lead Svc │   │    │
│  │  └────┬─────┘  └──────────┘  └──────────┘   │    │
│  │       │         ┌──────────┐                  │    │
│  │       │         │ Ringover │                  │    │
│  │       │         │  Service │                  │    │
│  │       │         └────┬─────┘                  │    │
│  └───────┼──────────────┼────────────────────────┘    │
│          │              │                              │
│  ┌───────▼──────────────▼────────────────────────┐    │
│  │           DATABASE (SQLAlchemy async)           │    │
│  │     SQLite (dev) / PostgreSQL (prod)           │    │
│  └────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────┘
           │                      │
    ┌──────▼──────┐       ┌──────▼──────┐
    │   OpenAI    │       │  Ringover   │
    │    API      │       │    API v2   │
    │ GPT/TTS/STT │       │ Calls/Users │
    └─────────────┘       └─────────────┘
```

### 2.3 Modèle de données

**Call** (appels)
- Identifiants : id, ringover_call_id
- Numéros : caller_number, called_number
- Statuts : status, direction
- IVR/IA : ivr_choice, transcript, ai_summary, ai_messages_json
- Transfert : transfer_to, transferred_at
- Relations : campaign_id, lead_id
- Timestamps : started_at, answered_at, ended_at, created_at, updated_at

**Lead** (prospects)
- Identité : first_name, last_name, phone, email
- Qualification : interest, score, status, budget, urgency
- Métadonnées : source, is_archived, notes
- Relation : calls (one-to-many)

**Campaign** (campagnes)
- Identité : name, description, type, status
- Configuration : ai_system_prompt, ivr_message, target_interest, target_region
- Métriques : total_calls, answered_calls, missed_calls, transferred_calls, leads_generated, conversion_rate
- Relation : calls (one-to-many)

**Configuration** (paramètres)
- Clé-valeur : key, value, category, label, description
- Sécurité : is_secret (masquage des valeurs sensibles)

---

## 3. Flux des données

### 3.1 Flux d'un appel entrant complet

```
1. Téléphone sonne → Ringover envoie webhook /incoming
2. Système crée un Call en BDD + session IA
3. IVR joué → client appuie sur une touche
4. Ringover envoie webhook /dtmf
5. Système traite le choix IVR, route vers l'agent IA
6. Client parle → Ringover transcrit → webhook /speech
7. Agent IA répond (GPT-4o) + extrait les données lead
8. Lead créé/mis à jour en BDD avec scoring
9. Si score ≥ 70 : transfert proposé vers agent humain
10. Appel terminé → webhook /hangup ou /status
11. Résumé IA généré et sauvegardé
12. Session IA nettoyée
```

### 3.2 Flux de qualification

```
Données brutes client (parole) 
  → Transcription (Whisper STT)
    → Analyse IA (GPT-4o)
      → Extraction structurée <LEAD_DATA>
        → Scoring (0-100)
          → Catégorisation (hot/warm/qualified/cold)
            → Décision : transfert ou poursuite conversation
```

---

## 4. Sécurité

### 4.1 Authentification API

- Clés API stockées dans les variables d'environnement (.env)
- Les clés sensibles sont masquées dans l'interface de configuration
- Validation HMAC SHA-256 des webhooks Ringover (optionnel)

### 4.2 Protection des données

- Les mots de passe et clés ne sont jamais logués
- Les secrets sont masqués par "***" dans l'API de configuration
- CORS configurable pour restreindre les origines en production
- Pas de données personnelles dans les logs

### 4.3 Recommandations production

- Utiliser HTTPS obligatoirement (via Nginx reverse proxy)
- Changer SECRET_KEY à une valeur aléatoire de 32+ caractères
- Configurer CORS_ORIGINS avec les domaines autorisés uniquement
- Configurer RINGOVER_WEBHOOK_SECRET pour valider les webhooks
- Utiliser PostgreSQL au lieu de SQLite en production

---

## 5. Déploiement

### 5.1 Prérequis serveur

- Linux (Ubuntu 22.04+ recommandé)
- Python 3.11+
- pip + venv
- Nginx (reverse proxy HTTPS)
- Accès SSH et ports 80/443 ouverts

### 5.2 Procédure

1. Transfert des fichiers via FileZilla (SFTP)
2. Installation des dépendances Python
3. Configuration du fichier .env
4. Création du service systemd
5. Configuration Nginx + certificat SSL
6. Configuration des webhooks dans Ringover
7. Test de bout en bout via le simulateur

### 5.3 Monitoring

- Endpoint `/health` pour les health checks
- Logs d'accès et d'erreur dans `logs/`
- Dashboard de l'application pour le suivi temps réel

---

## 6. Évolutions prévues

- Authentification utilisateur (login/rôles)
- Support multi-tenant
- Campagnes outbound (appels sortants automatisés)
- Intégration CRM (Salesforce, HubSpot)
- Statistiques avancées et rapports exportables
- WebSocket pour le temps réel sans polling
