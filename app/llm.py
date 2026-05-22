import os
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from app.config import (
    GROQ_API_KEY, GOOGLE_API_KEY,
    GROQ_CHAT_MODEL, GEMINI_CHAT_MODEL,
)

try:
    from langchain_groq import ChatGroq
except Exception:
    ChatGroq = None

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except Exception:
    ChatGoogleGenerativeAI = None


def build_llm():
    if ChatGroq is not None and GROQ_API_KEY:
        print(f"[LLM] Using Groq — {GROQ_CHAT_MODEL}")
        return ChatGroq(
            model=GROQ_CHAT_MODEL,
            api_key=GROQ_API_KEY,
            temperature=0.2,
            max_tokens=512,
        )

    if ChatGoogleGenerativeAI is not None and GOOGLE_API_KEY:
        print(f"[LLM] Groq unavailable — falling back to Gemini {GEMINI_CHAT_MODEL}")
        return ChatGoogleGenerativeAI(
            model=GEMINI_CHAT_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=0.2,
            max_output_tokens=512,
        )

    raise RuntimeError(
        "No LLM available. Set GROQ_API_KEY or GOOGLE_API_KEY in your .env file."
    )


def active_model_name() -> str:
    if ChatGroq is not None and GROQ_API_KEY:
        return GROQ_CHAT_MODEL
    if ChatGoogleGenerativeAI is not None and GOOGLE_API_KEY:
        return GEMINI_CHAT_MODEL
    return "none"


SYSTEM_PROMPT = """You are RewardBot, the friendly AI assistant for the RewardPlus loyalty program.
You help members understand their rewards, transaction points, and program policies.

Guidelines:
- Always cite the specific policy section when explaining rules (e.g. "Per Section 3 of our Rewards Policy...")
- When a transaction is described, calculate points clearly: Amount x Base Rate x Multiplier = Points
- If a question is outside the rewards program scope, politely redirect
- Keep answers concise but complete
- If the retrieved context does not cover the question, say so honestly

Retrieved policy context:
{context}

Conversation history:
{chat_history}"""


def build_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template("{question}"),
    ])