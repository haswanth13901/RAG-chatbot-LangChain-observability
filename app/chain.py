from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import Chroma

from app.config import MEMORY_WINDOW, RETRIEVAL_K
from app.prompts import build_prompt, build_blocked_prompt
from app.security import check_injection


class RAGChatSession:
    def __init__(self, vectorstore: Chroma, llm):
        self.retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": RETRIEVAL_K, "fetch_k": 12},
        )
        self.llm             = llm
        self.history:  list  = []
        self.source_documents: list = []
        self.prompt          = build_prompt()
        self.blocked_prompt  = build_blocked_prompt()
        self.parser          = StrOutputParser()

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

    def invoke(self, question: str) -> str:
        security = check_injection(question)

        if not security.is_safe:
            print(f"[SECURITY] Blocked — {security.reason}")
            blocked_chain = self.blocked_prompt | self.llm | self.parser
            answer = blocked_chain.invoke({"question": question})
            
            return answer

        clean_question = security.sanitized

        docs    = self.retriever.invoke(clean_question)
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


def extract_sources(session: "RAGChatSession") -> list[str]:
    return session.get_sources()