from typing import Any
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma

from app.config import MEMORY_WINDOW, RETRIEVAL_K
from app.prompts import SYSTEM_PROMPT


class RAGChatSession:
    """
    Manages a single user's RAG conversation.
    Replaces ConversationalRetrievalChain with a simple
    LCEL chain + manual history — compatible with all LangChain versions.
    """

    def __init__(self, vectorstore: Chroma, llm: ChatGoogleGenerativeAI):
        self.retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": RETRIEVAL_K, "fetch_k": 12},
        )
        self.llm      = llm
        self.history: list[dict] = []
        self.source_documents: list   = []

        self.prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)
        self.parser = StrOutputParser()

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
        docs    = self.retriever.invoke(question)
        context = self._format_docs(docs)
        history = self._format_history()

        chain  = self.prompt | self.llm | self.parser
        answer = chain.invoke({
            "context":      context,
            "chat_history": history,
            "question":     question,
        })

        self.history.append({"role": "user",      "content": question})
        self.history.append({"role": "assistant",  "content": answer})

        return answer

    def get_sources(self) -> list[str]:
        return list({
            doc.metadata.get("source_file", "policy")
            for doc in self.source_documents
        })


def extract_sources(session: "RAGChatSession") -> list[str]:
    return session.get_sources()