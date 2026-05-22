from typing import Any
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma

from app.config import MEMORY_WINDOW, RETRIEVAL_K


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
{chat_history}

Question: {question}"""


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