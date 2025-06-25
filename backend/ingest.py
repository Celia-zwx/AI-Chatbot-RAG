"""Load PDF files from local folder, clean up, split, ingest into Weaviate."""
import logging
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.indexes import SQLRecordManager, index
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Weaviate
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
import weaviate
from constants import WEAVIATE_DOCS_INDEX_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_embeddings_model() -> Embeddings:
    return OpenAIEmbeddings(model="text-embedding-3-small", chunk_size=200)


def load_local_pdf_docs(pdf_dir: str) -> list[Document]:
    all_docs = []
    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            path = os.path.join(pdf_dir, filename)
            loader = PyPDFLoader(path)
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = path
                doc.metadata["title"] = os.path.basename(path)
            all_docs.extend(docs)
    return all_docs


def ingest_docs():
    WEAVIATE_URL = os.environ["WEAVIATE_URL"]
    WEAVIATE_API_KEY = os.environ["WEAVIATE_API_KEY"]
    RECORD_MANAGER_DB_URL = os.environ["RECORD_MANAGER_DB_URL"]
    PDF_DIR = os.environ.get("PDF_DIR", "./data/pdfs")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=200)
    embedding = get_embeddings_model()

    client = weaviate.Client(
        url=WEAVIATE_URL,
        auth_client_secret=weaviate.AuthApiKey(api_key=WEAVIATE_API_KEY),
    )
    print("Weaviate Ready:", client.is_ready())

    vectorstore = Weaviate(
        client=client,
        index_name=WEAVIATE_DOCS_INDEX_NAME,
        text_key="text",
        embedding=embedding,
        by_text=False,
        attributes=["source", "title"],
    )

    record_manager = SQLRecordManager(
        f"weaviate/{WEAVIATE_DOCS_INDEX_NAME}", db_url=RECORD_MANAGER_DB_URL
    )
    record_manager.create_schema()

    docs = load_local_pdf_docs(PDF_DIR)
    logger.info(f"Loaded {len(docs)} docs from local PDFs")

    docs_transformed = text_splitter.split_documents(docs)
    docs_transformed = [doc for doc in docs_transformed if len(doc.page_content) > 10]

    for doc in docs_transformed:
        doc.metadata.setdefault("source", "")
        doc.metadata.setdefault("title", "")

    indexing_stats = index(
        docs_transformed,
        record_manager,
        vectorstore,
        cleanup="full",
        source_id_key="source",
        force_update=(os.environ.get("FORCE_UPDATE") or "false").lower() == "true",
    )

    logger.info(f"Indexing stats: {indexing_stats}")
    num_vecs = client.query.aggregate(WEAVIATE_DOCS_INDEX_NAME).with_meta_count().do()
    logger.info(f"LangChain now has this many vectors: {num_vecs}")


if __name__ == "__main__":
    ingest_docs()
