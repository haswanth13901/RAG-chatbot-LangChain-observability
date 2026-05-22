from typing import Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: list[str]
    timestamp: str


class TransactionRequest(BaseModel):
    session_id: str
    transaction_id: str
    user_id: str
    type: str
    amount: float
    category: Optional[str] = None
    merchant: Optional[str] = None


class TransactionResponse(BaseModel):
    transaction_id: str
    points_earned: int
    multiplier_applied: float
    reward_tier: str
    chatbot_explanation: str
    sources: list[str]
    timestamp: str