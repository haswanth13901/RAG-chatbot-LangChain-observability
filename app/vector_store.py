from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

try:
    from langchain_community.document_loaders import Docx2txtLoader, DirectoryLoader
except ModuleNotFoundError as exc:
    raise RuntimeError(
        "Missing required package 'docx2txt'. Install it with `pip install docx2txt` "
        "or add it to requirements.txt and reinstall dependencies."
    ) from exc

from app.config import GOOGLE_API_KEY, EMBED_MODEL, DOCS_DIR, CHROMA_DIR


def load_and_split_documents() -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=60,
        separators=["\n\n", "\n", ".", " "],
    )
    all_docs: list[Document] = []

    if not DOCS_DIR.exists():
        raise FileNotFoundError(
            f"Document directory not found at {DOCS_DIR}. Create it and add your .docx policy files."
        )

    docx_files = list(DOCS_DIR.glob("*.docx"))
    if not docx_files:
        raise RuntimeError(
            f"No .docx files found in {DOCS_DIR}. Place RewardPlus policy docs there."
        )

    for docx_file in docx_files:
        loader = Docx2txtLoader(str(docx_file))
        try:
            raw_docs = loader.load()
        except ModuleNotFoundError as exc:
            if exc.name == "docx2txt":
                raise RuntimeError(
                    "The 'docx2txt' package is required to load .docx files. "
                    "Install it with `pip install docx2txt` or update requirements.txt."
                ) from exc
            raise
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


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        model=EMBED_MODEL,
        google_api_key=GOOGLE_API_KEY,
    )


class SafeGoogleGenerativeAIEmbeddings(GoogleGenerativeAIEmbeddings):
    def embed_documents(self, texts, *args, **kwargs):
        embeddings_list = super().embed_documents(texts, *args, **kwargs)
        if len(embeddings_list) != len(texts):
            print(
                "[EMBED] batch embed count mismatch; embedding each document separately"
            )
            embeddings_list = [
                super().embed_documents([text], *args, **kwargs)[0]
                for text in texts
            ]
        return embeddings_list


def build_vectorstore(docs: list[Document]) -> Chroma:
    embeddings = SafeGoogleGenerativeAIEmbeddings(
        model=EMBED_MODEL,
        google_api_key=GOOGLE_API_KEY,
    )

    if CHROMA_DIR.exists() and any(CHROMA_DIR.iterdir()):
        try:
            vectorstore = Chroma(
                persist_directory=str(CHROMA_DIR),
                embedding_function=embeddings,
            )
            existing_count = vectorstore._collection.count()
            if existing_count > 0:
                print("[VECTOR] Loading existing ChromaDB from disk")
                return vectorstore

            print("[VECTOR] Existing ChromaDB is empty; removing stale database and rebuilding")
            vectorstore = None
        except Exception:
            print("[VECTOR] Existing ChromaDB appears corrupted; removing stale database and rebuilding")
            vectorstore = None

        import shutil
        shutil.rmtree(str(CHROMA_DIR), ignore_errors=True)

    print(f"[VECTOR] Building ChromaDB from {len(docs)} chunks")
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
    )
    return vectorstore