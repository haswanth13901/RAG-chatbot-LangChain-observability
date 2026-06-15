from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app.config import (
    GOOGLE_API_KEY, EMBED_MODEL,
    DOCS_DIR, CHROMA_DIR,
    RETRIEVAL_K, SIMILARITY_THRESHOLD,
)


def load_and_split_documents() -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=60,
        separators=["\n\n", "\n", ".", " "],
    )
    all_docs: list[Document] = []

    if not DOCS_DIR.exists():
        raise FileNotFoundError(f"Docs directory not found: {DOCS_DIR}")

    docx_files = list(DOCS_DIR.glob("*.docx"))
    if not docx_files:
        raise RuntimeError(f"No .docx files found in {DOCS_DIR}")

    for docx_file in docx_files:
        loader   = Docx2txtLoader(str(docx_file))
        raw_docs = loader.load()
        for doc in raw_docs:
            doc.metadata["source_file"] = docx_file.name
            doc.metadata["doc_type"]    = (
                "rewards_policy" if "reward" in docx_file.name.lower()
                else "terms_conditions"
            )
        chunks = splitter.split_documents(raw_docs)
        all_docs.extend(chunks)
        print(f"[INGEST] {docx_file.name} → {len(chunks)} chunks")

    return all_docs


class SafeGoogleGenerativeAIEmbeddings(GoogleGenerativeAIEmbeddings):
    def embed_documents(self, texts, *args, **kwargs):
        embeddings_list = super().embed_documents(texts, *args, **kwargs)
        if len(embeddings_list) != len(texts):
            embeddings_list = [
                super().embed_documents([text], *args, **kwargs)[0]
                for text in texts
            ]
        return embeddings_list


def get_embeddings() -> SafeGoogleGenerativeAIEmbeddings:
    return SafeGoogleGenerativeAIEmbeddings(
        model=EMBED_MODEL,
        google_api_key=GOOGLE_API_KEY,
    )


def build_vectorstore(docs: list[Document]) -> Chroma:
    embeddings = get_embeddings()

    if CHROMA_DIR.exists() and any(CHROMA_DIR.iterdir()):
        try:
            vectorstore    = Chroma(
                persist_directory=str(CHROMA_DIR),
                embedding_function=embeddings,
            )
            existing_count = vectorstore._collection.count()
            if existing_count > 0:
                print("[VECTOR] Loading existing ChromaDB from disk")
                return vectorstore
        except Exception:
            pass

        import shutil
        shutil.rmtree(str(CHROMA_DIR), ignore_errors=True)

    print(f"[VECTOR] Building ChromaDB from {len(docs)} chunks")
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
    )
    return vectorstore


def retrieve_with_threshold(
    vectorstore: Chroma,
    query: str,
    k: int = RETRIEVAL_K,
    threshold: float = SIMILARITY_THRESHOLD,
) -> tuple[list[Document], list[float]]:
    scored_docs = vectorstore.similarity_search_with_relevance_scores(query, k=k)

    filtered = [
        (doc, score)
        for doc, score in scored_docs
        if score >= threshold
    ]

    if not filtered:
        print(f"[THRESHOLD] No chunks passed threshold {threshold} — scores: {[round(s,3) for _,s in scored_docs]}")
        return [], []

    docs, scores = zip(*filtered)
    print(f"[THRESHOLD] {len(docs)}/{k} chunks passed (threshold={threshold}) — scores: {[round(s,3) for s in scores]}")
    return list(docs), list(scores)