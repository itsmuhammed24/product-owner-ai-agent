# Challenges & solutions

## Design agentique

| Concept | Implémentation |
|---------|----------------|
| **LangGraph** | StateGraph 7 nœuds, conditional edges |
| **Reasoning loop** | CritiqueAgent (LLM-as-a-judge) → refine si score < 4, max 2 passes |
| **RAG** | RetrievalAgent + Chroma (persistance) |
| **Human-in-the-loop** | `stop_at=insights|backlog` |
| **ReAct / tools** | Chat : détection d'intent → What-if, Roadmap, recherche |

---

## Problèmes résolus

### Outputs LLM non structurés
**Solution** : Extraction JSON, validation Pydantic, retry.

### Regroupement requêtes similaires
**Solution** : Normalisation + clustering sémantique (OpenAI embeddings optionnel).

### Explicabilité
**Solution** : Rationale, Evidence IDs, onglet Explainability.

### Warnings au démarrage

| Warning | Cause | Action |
|---------|-------|--------|
| `You are sending unauthenticated requests to the HF Hub` | HuggingFace rate limits | Optionnel : définir `HF_TOKEN` dans `.env` (https://huggingface.co/settings/tokens) |
| `BertModel … embeddings.position_ids UNEXPECTED` | Différence mineure de config du modèle | **Ignorable** — sentence-transformers fonctionne correctement |
