import hashlib
from typing import Optional
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma

from app.config import (
    MEMORY_WINDOW, RETRIEVAL_K,
    SIMILARITY_THRESHOLD, MIN_RELEVANT_CHUNKS,
    RERANK_TOP_N,
)
from app.prompts import build_prompt, build_blocked_prompt
from app.security import check_injection
from app.vector_store import retrieve_with_threshold

try:
    from langchain_community.document_compressors import FlashrankRerank
    _reranker = FlashrankRerank(top_n=RERANK_TOP_N)
    print("[RERANK] FlashrankRerank loaded successfully")
except Exception as e:
    _reranker = None
    print(f"[RERANK] FlashrankRerank unavailable — skipping rerank step ({e})")

INSUFFICIENT_CONTEXT_RESPONSE = (
    "I wasn't able to find enough relevant information in the RewardPlus "
    "policy documents to answer your question confidently. "
    "Please try rephrasing your question or contact our support team "
    "for assistance with this specific query."
)


def deduplicate(docs: list[Document]) -> list[Document]:
    seen:   set  = set()
    unique: list = []
    for doc in docs:
        content_hash = hashlib.md5(doc.page_content.strip().encode()).hexdigest()
        if content_hash not in seen:
            seen.add(content_hash)
            unique.append(doc)
    removed = len(docs) - len(unique)
    if removed > 0:
        print(f"[DEDUP] Removed {removed} duplicate chunk(s) — {len(unique)} unique remaining")
    return unique


def rerank(docs: list[Document], query: str) -> list[Document]:
    if not _reranker or len(docs) <= 1:
        return docs
    try:
        reranked = _reranker.compress_documents(docs, query)
        print(f"[RERANK] {len(docs)} chunks → top {len(reranked)} after reranking")
        return list(reranked)
    except Exception as e:
        print(f"[RERANK] Failed — using original order ({e})")
        return docs


class RAGChatSession:
    def __init__(self, vectorstore: Chroma, llm):
        self.vectorstore            = vectorstore
        self.llm                    = llm
        self.history: list          = []
        self.source_documents: list = []
        self.last_scores: list      = []
        self.prompt                 = build_prompt()
        self.blocked_prompt         = build_blocked_prompt()
        self.parser                 = StrOutputParser()

    def _format_history(self) -> str:
        if not self.history:
            return "No previous conversation."
        lines = []
        for msg in self.history[-(MEMORY_WINDOW * 2):]:
            role = "User" if msg["role"] == "user" else "RewardBot"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)

    def _format_docs(self, docs) -> str:
        self.source_documents = docs
        return "\n\n---\n\n".join(doc.page_content for doc in docs)

    def _is_sufficient(self, docs: list) -> bool:
        sufficient = len(docs) >= MIN_RELEVANT_CHUNKS
        if not sufficient:
            print(f"[SUFFICIENCY] Only {len(docs)} chunk(s) — minimum is {MIN_RELEVANT_CHUNKS}")
        return sufficient

    def invoke(self, question: str, doc_filter: Optional[str] = None) -> str:
        security = check_injection(question)
        if not security.is_safe:
            print(f"[SECURITY] Blocked — {security.reason}")
            blocked_chain = self.blocked_prompt | self.llm | self.parser
            return blocked_chain.invoke({"question": question})

        clean_question = security.sanitized

        docs, scores = retrieve_with_threshold(
            vectorstore=self.vectorstore,
            query=clean_question,
            k=RETRIEVAL_K,
            threshold=SIMILARITY_THRESHOLD,
            doc_filter=doc_filter,
        )
        self.last_scores = scores

        docs = deduplicate(docs)

        if not self._is_sufficient(docs):
            print(f"[SUFFICIENCY] Insufficient context — returning fallback response")
            return INSUFFICIENT_CONTEXT_RESPONSE

        docs = rerank(docs, clean_question)

        context = self._format_docs(docs)
        history = self._format_history()

        chain  = self.prompt | self.llm | self.parser
        answer = chain.invoke({
            "context":      context,
            "chat_history": history,
            "question":     clean_question,
        })

        self.history.append({"role": "user",      "content": clean_question})
        self.history.append({"role": "assistant",  "content": answer})

        return answer

    def get_sources(self) -> list[str]:
        return list({
            doc.metadata.get("source_file", "policy")
            for doc in self.source_documents
        })

    def get_last_scores(self) -> list[float]:
        return [round(s, 3) for s in self.last_scores]