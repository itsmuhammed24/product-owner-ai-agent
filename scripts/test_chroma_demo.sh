#!/bin/bash
# Test Chroma : 2 analyses successives pour vérifier la persistance
# Prérequis : API lancée (make start) sur http://localhost:8000
# Utilise data/demo/feedback_chroma_session1.jsonl et session2.jsonl

set -e
cd "$(dirname "$0")/.."
API="${API_URL:-http://localhost:8000}"

SESSION1="data/demo/feedback_chroma_session1.jsonl"
SESSION2="data/demo/feedback_chroma_session2.jsonl"

if [ ! -f "$SESSION1" ] || [ ! -f "$SESSION2" ]; then
  echo "Erreur: $SESSION1 ou $SESSION2 introuvable"
  exit 1
fi

echo "=== Test Chroma Demo ==="
echo "API: $API"
echo ""

echo "1. Analyse 1 — session 1 (stocke dans Chroma)..."
CONTENT=$(jq -Rs . < "$SESSION1")
FEEDBACK=$(curl -s -X POST "$API/ingest" \
  -H "Content-Type: application/json" \
  -d "{\"content\": $CONTENT, \"format\": \"jsonl\"}")
COUNT=$(echo "$FEEDBACK" | jq -r '.count')
echo "   Ingesté: $COUNT feedbacks"

PAYLOAD1=$(echo "$FEEDBACK" | jq -c '{feedback: .feedback}')
RUN1=$(curl -s -X POST "$API/run" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD1")
echo "   Insights: $(echo "$RUN1" | jq '.insights | length')"

echo ""
echo "2. Analyse 2 — session 2 (Chroma enrichit avec l'historique)..."
CONTENT2=$(jq -Rs . < "$SESSION2")
FEEDBACK2=$(curl -s -X POST "$API/ingest" \
  -H "Content-Type: application/json" \
  -d "{\"content\": $CONTENT2, \"format\": \"jsonl\"}")
PAYLOAD2=$(echo "$FEEDBACK2" | jq -c '{feedback: .feedback}')
RUN2=$(curl -s -X POST "$API/run" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD2")

echo "   Insights: $(echo "$RUN2" | jq '.insights | length')"
echo "   Stories: $(echo "$RUN2" | jq '.stories | length')"
echo ""
echo "3. Vérification Chroma..."
if [ -d "./data/chroma" ] && [ -n "$(ls -A ./data/chroma 2>/dev/null)" ]; then
  echo "   OK — ./data/chroma contient des données"
  ls -la ./data/chroma/
else
  echo "   Dossier Chroma vide ou absent (USE_CHROMA=true ?)"
fi

echo ""
echo "=== Demo terminée ==="
