# Stack technique

## Vue d'ensemble

| Couche | Technologie | Version | Rôle |
|--------|-------------|---------|------|
| **Backend** | Python | 3.10+ | API, pipeline IA |
| **API** | FastAPI | 0.109+ | REST, validation Pydantic |
| **Orchestration** | LangGraph | 0.0.20+ | Pipeline agentique |
| **LLM** | Groq | API | Modèles Llama (gratuit) |
| **RAG** | sentence-transformers | 2.2+ | Embeddings all-MiniLM-L6-v2 |
| **Vector store** | ChromaDB | 0.4+ | Persistance RAG (optionnel) |
| **Frontend** | React | 19 | UI |
| **Build** | Vite | 7 | Bundler frontend |
| **Styling** | Tailwind CSS | 3.4 | UI |

---

## Références officielles

| Techno | Documentation |
|--------|---------------|
| **FastAPI** | [fastapi.tiangolo.com](https://fastapi.tiangolo.com) |
| **LangGraph** | [langchain-ai.github.io/langgraph](https://langchain-ai.github.io/langgraph) |
| **Groq** | [console.groq.com](https://console.groq.com) |
| **ChromaDB** | [docs.trychroma.com](https://docs.trychroma.com) |
| **sentence-transformers** | [sbert.net](https://www.sbert.net) |
| **React** | [react.dev](https://react.dev) |
| **Vite** | [vitejs.dev](https://vitejs.dev) |
| **Pydantic** | [docs.pydantic.dev](https://docs.pydantic.dev) |

---

## Dépendances Python (pyproject.toml)

```
pydantic>=2.5.0
openai>=1.0.0        # client Groq (API compatible)
fastapi>=0.109.0
uvicorn[standard]
langgraph>=0.0.20
python-dotenv
requests
```

**Optionnelles** :
- `.[rag]` — sentence-transformers (RetrievalAgent)
- `.[chroma]` — chromadb + sentence-transformers
- `.[dev]` — pytest, ruff, pre-commit
