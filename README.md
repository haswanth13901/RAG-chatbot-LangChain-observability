# Production RAG Chatbot — LangChain · Groq · ChromaDB · Observability

**End-to-end Retrieval-Augmented Generation system** with conversational AI,
semantic document search, transaction reward processing, and a full
monitoring and observability pipeline — built with LangChain, Groq LLaMA,
Google Gemini Embeddings, ChromaDB, and FastAPI.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green)
![LangChain](https://img.shields.io/badge/LangChain-1.3+-yellow)
![Groq](https://img.shields.io/badge/Groq-LLaMA3.1-orange)
![ChromaDB](https://img.shields.io/badge/ChromaDB-1.5+-red)
![Status](https://img.shields.io/badge/Phase%201-Complete-brightgreen)
![Status](https://img.shields.io/badge/Phase%202-In%20Progress-yellow)

---

## Project Phases

| Phase | Description | Status |
|---|---|---|
| [Phase 1 — RAG Chatbot](/) | LangChain + Groq + ChromaDB | ✅ Complete |
| [Phase 2 — Monitoring](monitoring/) | Observability + CI/CD | 🚧 In Progress |

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Minimum Hardware Requirements](#minimum-hardware-requirements)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Example Requests](#example-requests)
- [Architecture](#architecture)
- [Reward Rules](#reward-rules)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)

---

## Overview

A production-ready conversational AI system designed to help loyalty program members understand their rewards. It leverages **Retrieval-Augmented Generation** to combine large language models with curated policy documents, ensuring accurate, citation-backed responses.

The system supports:
- **Multi-user sessions** with conversation memory
- **Transaction analysis** with automatic point calculation
- **Intelligent retrieval** using semantic search via ChromaDB
- **Flexible LLM selection** with automatic fallback mechanisms

---

## Features

- 🤖 **RAG-Powered Chatbot** — Answers grounded in actual policy documents
- 💬 **Conversation Management** — Session history for coherent multi-turn dialogues
- 💰 **Transaction Processing** — Points calculation with category-based multipliers
- 🔄 **Multi-Model Support** — Groq LLaMA (primary) with Google Gemini fallback
- 🧠 **Vector Search** — ChromaDB with Gemini embeddings for semantic retrieval
- 📊 **Session Tracking** — Per-user sessions with configurable memory windows
- ✅ **Health Monitoring** — Built-in endpoint for system status and model info
- 🚀 **FastAPI REST API** — Async, typed endpoints with Pydantic validation

---

## Tech Stack

### Core Framework
- **Python 3.10+**
- **FastAPI 0.115+** — Modern async web framework
- **Uvicorn 0.47+** — ASGI server

### AI & NLP
- **LangChain 1.3+** — LLM orchestration and RAG pipeline
- **LangChain Groq 1.1+** — Groq LLaMA integration (primary chat)
- **LangChain Google GenAI 4.2+** — Gemini embeddings
- **ChromaDB 1.5+** — In-process vector database

### Data & Validation
- **Pydantic 2.8+** — Request/response validation
- **LangChain Text Splitters 1.1+** — Document chunking
- **Docx2txt 0.8** — Word document parsing

### Utilities
- **Python-dotenv 1.2+** — Environment variable management
- **HTTPx 0.28+** — Async HTTP client

---

## Minimum Hardware Requirements

| Component | Minimum | Recommended |
|---|---|---|
| **CPU** | Dual-core 1.8 GHz | Quad-core 2.5 GHz+ (e.g. i7-10510U) |
| **RAM** | 4 GB | 8 GB+ |
| **Storage** | 2 GB free | 5 GB free |
| **OS** | Windows 10 / macOS 11 / Ubuntu 20.04 | Windows 11 / macOS 13 / Ubuntu 22.04 |
| **Python** | 3.10 | 3.12 |
| **Internet** | Required | Stable broadband |

> **No GPU required.** All LLM inference runs via Groq/Gemini APIs. ChromaDB runs in-process — no Docker or external database needed.

### RAM Usage Breakdown

| Component | Approx. RAM |
|---|---|
| Python + FastAPI | ~150 MB |
| ChromaDB in-process | ~200 MB |
| LangChain + dependencies | ~300 MB |
| OS overhead | ~1 GB |
| **Total active** | **~1.6 GB** |

8 GB is comfortable. 4 GB is workable — avoid running other heavy apps simultaneously.

---

## Project Structure

```
rag-chatbot-langchain-observability/
├── main.py                        # FastAPI app, routes, session management
├── test_chatbot.py                # CLI demo and interactive REPL
├── requirements.txt               # Python dependencies
├── .env                           # API keys (never committed)
├── .env.example                   # Template for required keys
├── .gitignore
├── README.md
│
├── app/
│   ├── __init__.py
│   ├── config.py                  # Settings, reward rules, API keys
│   ├── models.py                  # Pydantic request/response schemas
│   ├── llm.py                     # LLM init, system prompt, fallback logic
│   ├── chain.py                   # RAGChatSession — retrieval + generation
│   ├── vector_store.py            # ChromaDB setup, document ingestion
│   └── rewards.py                 # Points calculation engine
│
├── Docs/                          # Policy documents (.docx)
│   ├── RewardPlus_Rewards_Policy.docx
│   └── RewardPlus_Terms_and_Conditions.docx
│
└── chroma_db/                     # Auto-generated vector index (not committed)
```

---

## Installation & Setup

### Prerequisites

- Python 3.10+
- **Windows only:** Microsoft C++ Build Tools (required for ChromaDB)
  - Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
  - Select: **Desktop development with C++** workload
- API keys for Google (embeddings) and Groq (chat)

### Step 1 — Clone the Repository

```bash
git clone https://github.com/yourusername/rag-chatbot-langchain-observability.git
cd rag-chatbot-langchain-observability
```

### Step 2 — Create Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4 — Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env`:
```env
GOOGLE_API_KEY=your_google_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

Get your free API keys:
- Google: https://aistudio.google.com/apikey
- Groq: https://console.groq.com

### Step 5 — Add Policy Documents

```
Docs/
├── RewardPlus_Rewards_Policy.docx
└── RewardPlus_Terms_and_Conditions.docx
```

The server automatically loads, chunks, and embeds these on startup.

---

## Configuration

All settings in `app/config.py`:

| Variable | Default | Description |
|---|---|---|
| `GROQ_CHAT_MODEL` | `llama-3.1-8b-instant` | Primary chat model |
| `GEMINI_CHAT_MODEL` | `gemini-2.0-flash` | Fallback chat model |
| `EMBED_MODEL` | `gemini-embedding-2-preview` | Embedding model (always Gemini) |
| `MEMORY_WINDOW` | `10` | Conversation turns kept per session |
| `RETRIEVAL_K` | `4` | Policy chunks retrieved per query |
| `DOCS_DIR` | `./Docs` | Policy documents folder |
| `CHROMA_DIR` | `./chroma_db` | Vector index path |

### LLM Priority

```
1. Groq  (llama-3.1-8b-instant) ← primary   — 14,400 free req/day
2. Gemini (gemini-2.0-flash)    ← fallback  —  1,500 free req/day
3. RuntimeError                 ← no keys set
```

Gemini is always used for embeddings regardless of which model handles chat.

---

## Usage

### Start the Server

```bash
# Development
uvicorn main:app --reload --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

- Server: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

### Test the Chatbot

```bash
# Full demo — 4 scenes, all transaction types
python test_chatbot.py

# Interactive REPL — type questions live
python test_chatbot.py --interactive
```

---

## API Endpoints

### `POST /chat`
```json
{
  "session_id": "user-123",
  "message": "How many points do I earn on groceries?"
}
```
```json
{
  "session_id": "user-123",
  "answer": "Per Section 2 of our Rewards Policy, groceries earn a 2x multiplier — 20 points per dollar...",
  "sources": ["RewardPlus_Rewards_Policy.docx"],
  "timestamp": "2026-05-21T14:32:00Z"
}
```

### `POST /transaction/reward`
```json
{
  "session_id": "user-123",
  "transaction_id": "txn-456",
  "user_id": "user-123",
  "type": "purchase",
  "amount": 150.00,
  "category": "dining",
  "merchant": "Restaurant XYZ"
}
```
```json
{
  "transaction_id": "txn-456",
  "points_earned": 4500,
  "multiplier_applied": 3.0,
  "reward_tier": "dining",
  "chatbot_explanation": "You earned 4,500 points — $150 × 10 base × 3x dining multiplier...",
  "sources": ["RewardPlus_Rewards_Policy.docx"],
  "timestamp": "2026-05-21T14:32:00Z"
}
```

**Valid transaction types:** `purchase` `transfer` `bill_payment` `referral` `subscription`

### `DELETE /chat/{session_id}`
Clears conversation memory for a session.

### `GET /health`
```json
{
  "status": "ok",
  "chunks_indexed": 18,
  "active_sessions": 0,
  "chat_model": "llama-3.1-8b-instant",
  "embed_model": "gemini-embedding-2-preview",
  "google_key": true,
  "groq_key": true
}
```

### `GET /rewards/rules`
Returns the full reward rules table as JSON.

---

## Example Requests

### cURL

```bash
# Chat
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "demo", "message": "What is the dining multiplier?"}'

# Transaction
curl -X POST "http://localhost:8000/transaction/reward" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo",
    "transaction_id": "t-001",
    "user_id": "u-001",
    "type": "purchase",
    "amount": 50.00,
    "category": "groceries",
    "merchant": "Whole Foods"
  }'

# Health
curl "http://localhost:8000/health"

# Clear session
curl -X DELETE "http://localhost:8000/chat/demo"
```

### Python

```python
import httpx, asyncio

async def ask():
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "http://localhost:8000/chat",
            json={"session_id": "py-user", "message": "Do I earn points on bill payments?"}
        )
        print(r.json()["answer"])

asyncio.run(ask())
```

---

## Architecture

```
User Query
    ↓
FastAPI Router → Session Lookup / Create
    ↓
RAGChatSession.invoke(question)
    ↓
Retriever → ChromaDB MMR Search
    ↑                    ↓
Google Embeddings ← embed question
    ↓
Format prompt (context + history + question)
    ↓
Groq LLaMA (or Gemini fallback) → Generate answer
    ↓
Extract source documents → Return ChatResponse
```

| Component | File | Purpose |
|---|---|---|
| API Layer | `main.py` | HTTP routing, session management |
| RAG Session | `app/chain.py` | Retrieval + generation + memory |
| Vector Store | `app/vector_store.py` | ChromaDB setup, document ingestion |
| LLM | `app/llm.py` | Groq/Gemini init, system prompt |
| Reward Engine | `app/rewards.py` | Points calculation logic |
| Config | `app/config.py` | All settings and reward rules |
| Models | `app/models.py` | Pydantic schemas |

---

## Reward Rules

| Type | Base Rate | Bonus Categories |
|---|---|---|
| **Purchase** | 10 pts/$ | 🛒 Groceries 2x · 🍽️ Dining 3x · ✈️ Travel 5x · 📱 Electronics 1.5x |
| **Transfer** | 2 pts/$ | None |
| **Bill Payment** | 5 pts/$ | 💡 Utilities 1.5x · 🛡️ Insurance 2x |
| **Referral** | 500 pts flat | One-time per referred user |
| **Subscription** | 8 pts/$ | 🎬 Streaming 2x |

### Example Calculations

```
$100 Grocery Purchase  = $100 × 10 × 2x  = 2,000 points
$50  Dining            = $50  × 10 × 3x  = 1,500 points
$25  Streaming         = $25  × 8  × 2x  =   400 points
     Referral bonus    = 500 points flat
```

---

## Roadmap

- [ ] **Phase 2** — Monitoring & Observability (latency p50/p95/p99, token usage, CI/CD)
- [ ] PostgreSQL backend for persistent sessions
- [ ] Admin panel for managing reward rules without code changes
- [ ] Multi-language support
- [ ] Automated test coverage to 90%+
- [ ] Analytics dashboard for reward earning patterns

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'feat: your feature description'`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

**Guidelines:** Follow PEP 8 · Add docstrings · Test all endpoints · Update `requirements.txt` if adding deps

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `GOOGLE_API_KEY not found` | Add key to `.env` in project root |
| `No .docx files found` | Add policy files to `Docs/` folder |
| `ChromaDB corrupted` | Delete `chroma_db/` and restart |
| `429 RESOURCE_EXHAUSTED` | Gemini quota hit — Groq handles chat automatically |
| `chroma-hnswlib build error` | Install Microsoft C++ Build Tools (Windows) |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` inside `.venv` |
| `Out of memory` | Close other apps — need ~1.6 GB free RAM |

---

**Built with ❤️ as a Phase 1 RAG learning project — Phase 2 coming soon**
