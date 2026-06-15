import asyncio
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma

from app.config import GOOGLE_API_KEY, EMBED_MODEL, REWARD_RULES, validate_config
from app.vector_store import load_and_split_documents, build_vectorstore
from app.llm import build_llm, active_model_name
from app.chain import RAGChatSession
from app.rewards import calculate_points, build_reward_question
from app.access_control import verify_api_key
from app.models import (
    ChatRequest, ChatResponse,
    TransactionRequest, TransactionResponse,
)

app = FastAPI(
    title="RewardPlus RAG Chatbot",
    version="3.1.0",
    description="Production RAG Chatbot — LangChain · Groq · ChromaDB",
)

_sessions:    dict[str, RAGChatSession] = {}
_vectorstore: Optional[Chroma]          = None
_llm                                    = None


@app.on_event("startup")
async def startup():
    global _vectorstore, _llm

    warnings = validate_config()
    for w in warnings:
        print(f"[CONFIG WARNING] {w}")

    if not GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY not found. Check your .env file.")

    docs         = load_and_split_documents()
    _vectorstore = build_vectorstore(docs)
    _llm         = build_llm()
    print(f"[READY] {_vectorstore._collection.count()} chunks indexed | model: {active_model_name()}")


def get_or_create_session(session_id: str) -> RAGChatSession:
    if session_id not in _sessions:
        _sessions[session_id] = RAGChatSession(_vectorstore, _llm)
        print(f"[SESSION] Created: {session_id}")
    return _sessions[session_id]



@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, api_key: str = Depends(verify_api_key)):
    session = get_or_create_session(req.session_id)
    loop    = asyncio.get_event_loop()
    answer  = await loop.run_in_executor(
        None, lambda: session.invoke(req.message)
    )
    return ChatResponse(
        session_id=req.session_id,
        answer=answer,
        sources=session.get_sources(),
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@app.post("/transaction/reward", response_model=TransactionResponse)
async def process_transaction(
    req: TransactionRequest,
    api_key: str = Depends(verify_api_key),
):
    if req.type not in REWARD_RULES:
        raise HTTPException(
            400, f"Unknown type '{req.type}'. Valid: {list(REWARD_RULES.keys())}"
        )
    points, multiplier, tier = calculate_points(req.type, req.amount, req.category)
    question = build_reward_question(
        req.type, req.amount, points, multiplier, tier, req.category, req.merchant
    )
    session = get_or_create_session(req.session_id)
    loop    = asyncio.get_event_loop()
    answer  = await loop.run_in_executor(None, lambda: session.invoke(question))

    return TransactionResponse(
        transaction_id=req.transaction_id,
        points_earned=points,
        multiplier_applied=multiplier,
        reward_tier=tier,
        chatbot_explanation=answer,
        sources=session.get_sources(),
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@app.delete("/chat/{session_id}")
async def clear_session(
    session_id: str,
    api_key: str = Depends(verify_api_key),
):
    if session_id in _sessions:
        del _sessions[session_id]
        return {"status": "cleared", "session_id": session_id}
    return {"status": "not_found", "session_id": session_id}



@app.get("/health")
async def health():
    chunks = _vectorstore._collection.count() if _vectorstore else 0
    return {
        "status":          "ok",
        "chunks_indexed":  chunks,
        "active_sessions": len(_sessions),
        "chat_model":      active_model_name(),
        "embed_model":     EMBED_MODEL,
        "google_key":      bool(GOOGLE_API_KEY),
        "groq_key":        bool(__import__("os").getenv("GROQ_API_KEY")),
    }


@app.get("/rewards/rules")
async def reward_rules():
    return REWARD_RULES