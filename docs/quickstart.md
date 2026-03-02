# Quickstart

> Parcours pas-à-pas pour une première utilisation.

## Prérequis

- **Python 3.10+**
- **Node.js 18+** (pour l'UI)
- **Clé Groq** (gratuite) : [console.groq.com](https://console.groq.com)

---

## 1. Cloner et configurer

```bash
git clone <url-repo>
cd product-owner-ai-agent

# Créer le .env (obligatoire avant le lancement)
cp .env.example .env   # Windows : copy .env.example .env
```

Éditer `.env` et ajouter votre clé :

```
GROQ_API_KEY=gsk_xxx
```

---

## 2. Lancer

| Mode | Commande | URLs |
|------|----------|------|
| **Local** | `make start` | UI: http://localhost:5173 — API: http://localhost:8000 |
| **Docker** | `docker-compose up` | UI: http://localhost:80 — API via /api |

**Important** : pour Docker aussi, éditer `.env` et ajouter `GROQ_API_KEY` avant de lancer.

`make start` : crée le venv si besoin, installe les deps (Python + Node), lance API + UI. À la première exécution, l’installation peut prendre 1–2 min.

---

## 3. Première analyse

1. Ouvrir l'UI dans le navigateur (http://localhost:5173 ou http://localhost:80 en Docker)
2. Aller sur la page **Feedback**
3. Cliquer **Démo one-click** ou « Charger l'exemple »
4. Cliquer **Lancer l'analyse** (attendre ~30 s–1 min)
5. Voir les résultats : sidebar **Roadmap** (Insights, Backlog, Stories) et **Stories**
6. Télécharger le CSV Jira : page Stories, bouton d'export

**Données personnalisées** : uploader un fichier JSONL ou CSV (format : [api-reference](api-reference.md#format-des-données-import)).

**Assistant chat** : icône bulle en bas à droite pour poser des questions sur les résultats.

**En cas de problème** : [Dépannage](../README.md#dépannage).

---

## 4. API

- **Swagger** : http://localhost:8000/docs
- **Health** : `GET /health`
- **Ingest** : `POST /ingest` — `{"content": "...", "format": "jsonl"}`
- **Run** : `POST /run` — `{"feedback": [...]}`
