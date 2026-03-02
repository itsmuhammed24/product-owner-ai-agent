#!/bin/bash
# Une commande pour tout : setup + lancement
set -e
cd "$(dirname "$0")/.."

echo "PO Agent — setup + lancement"

# 1. Venv Python
if [ ! -d .venv ]; then
  echo "   Création venv..."
  python3 -m venv .venv
fi
. .venv/bin/activate

# 2. Deps Python
echo "   Install deps Python..."
pip install -q -e ".[dev,rag,chroma]"

# 3. Deps Node
if [ ! -d apps/web/node_modules ]; then
  echo "   Install deps Node..."
  (cd apps/web && npm install)
fi

# 4. .env
if [ ! -f .env ]; then
  cp .env.example .env
  echo "   .env créé (pense à ajouter GROQ_API_KEY)"
fi

echo ""
echo "   API : http://localhost:8000"
echo "   UI  : http://localhost:5173"
echo "   Ctrl+C pour arrêter"
echo ""

# 5. Lance
exec python scripts/dev.py
