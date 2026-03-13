#!/bin/bash
# ================================================================
#  NexCall AI — Script de démarrage production
#  Usage: ./scripts/start.sh
# ================================================================

set -e

echo "╔══════════════════════════════════════╗"
echo "║    NexCall AI — Démarrage Prod       ║"
echo "╚══════════════════════════════════════╝"

# Vérifier que le fichier .env existe
if [ ! -f .env ]; then
    echo "❌ Fichier .env manquant !"
    echo "   Copiez .env.example vers .env et configurez vos clés."
    echo "   cp .env.example .env"
    exit 1
fi

# Créer les dossiers nécessaires
mkdir -p data logs

# Vérifier Python
python3 --version || { echo "❌ Python3 non trouvé"; exit 1; }

# Installer les dépendances si nécessaire
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt --quiet

echo ""
echo "🚀 Démarrage du serveur..."
echo "   Dashboard: http://0.0.0.0:8000"
echo "   API docs:  http://0.0.0.0:8000/docs"
echo ""

# Démarrage avec Gunicorn + Uvicorn workers
gunicorn main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 4 \
    --bind 0.0.0.0:8000 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --timeout 120 \
    --graceful-timeout 30
