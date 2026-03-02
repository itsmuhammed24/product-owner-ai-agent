# LLM & providers

## Groq (par défaut)

- **Inscription** : [console.groq.com](https://console.groq.com)
- **Quota** : ~30 req/min, 14k req/jour (llama-3.1-8b-instant)
- **Coût** : Gratuit

```bash
GROQ_API_KEY=gsk_xxx
GROQ_MODEL=llama-3.1-8b-instant   # optionnel
```

---

## Options avancées

| Option | Rôle | Clé API |
|--------|------|---------|
| **RAG** | RetrievalAgent — features similaires | Non |
| **Chroma** | Persistance RAG cross-sessions | Non |
| **OpenAI embeddings** | Clustering sémantique InsightAgent | `OPENAI_API_KEY` |

Install : `pip install -e ".[chroma]"` (RAG + Chroma par défaut avec `make start`)
