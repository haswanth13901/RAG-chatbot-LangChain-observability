from typing import Optional, Literal
from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: str
    message:    str
    doc_filter: Optional[Literal["rewards_policy", "terms_conditions"]] = None


class ChatResponse(BaseModel):
    session_id: str
    answer:     str
    sources:    list[str]
    timestamp:  str
    doc_filter: Optional[str] = None


class TransactionRequest(BaseModel):
    session_id:     str
    transaction_id: str
    user_id:        str
    type:           str
    amount:         float
    category:       Optional[str] = None
    merchant:       Optional[str] = None


class TransactionResponse(BaseModel):
    transaction_id:      str
    points_earned:       int
    multiplier_applied:  float
    reward_tier:         str
    chatbot_explanation: str
    sources:             list[str]
    timestamp:           str