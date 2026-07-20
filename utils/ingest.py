import os
import glob
import warnings
from pathlib import Path
from dotenv import load_dotenv
from markitdown import MarkItDown
import httpx
import certifi

# Ingestion and embeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Milvus
from langchain_openai import AzureOpenAIEmbeddings

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*PyMilvus.*")

# Load environment
load_dotenv(override=True)

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
PDF_DIR = REPO_ROOT / "files_original"  # Source directory for original files (pdf, docx, pptx, etc.)
MD_DIR = REPO_ROOT / "files_md"
DB_NAME = str(REPO_ROOT / "vector_db")  # Not used by Milvus, kept for compatibility
KNOWLEDGE_BASE = str(MD_DIR)

# AskRegn / Azure-compatible embeddings (must match runtime)
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
if not ACCESS_TOKEN:
    raise RuntimeError("access_token is not set in environment")

# Set SSL certificate path for both sync and async clients
os.environ["SSL_CERT_FILE"] = certifi.where()

# Create custom HTTP client with certificate verification
http_client = httpx.Client(verify=certifi.where(), timeout=30.0)

embeddings = AzureOpenAIEmbeddings(
    api_key="AIR-API",
    azure_endpoint="https://air-api.regeneron.com/v1.0/model",
    api_version="2024-08-01-preview",
    azure_deployment="text-embed-3-large",
    default_headers={"authorization-token": ACCESS_TOKEN},
    http_client=http_client,
)

# Milvus settings from env (must match utils/answer.py)
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = int(os.getenv("MILVUS_PORT", "19530"))
MILVUS_USER = os.getenv("MILVUS_USER", "")
MILVUS_PASSWORD = os.getenv("MILVUS_PASSWORD", "")
MILVUS_DB_NAME = os.getenv("MILVUS_DB_NAME", "default")
MILVUS_SECURE = os.getenv("MILVUS_SECURE", "false").lower() == "true"
COLLECTION_NAME = os.getenv("MILVUS_COLLECTION", "files_md_embeddings")

def convert_files_to_md(
    src_dir: Path = PDF_DIR,
    out_dir: Path = MD_DIR,
    skip_existing: bool = True,
    supported_exts: tuple = ("pdf", "docx", "doc", "pptx", "ppt"),
) -> None:
    """
    Convert all supported files under src_dir to Markdown under out_dir, preserving directory structure.
    Skips already converted files when skip_existing is True.
    """
    md = MarkItDown()

    if not src_dir.exists():
        print(f"Source directory does not exist: {src_dir} (skipping conversion)")
        return

    candidates = []
    for ext in supported_exts:
        candidates.extend(sorted(src_dir.rglob(f"*.{ext}")))

    if not candidates:
        print(f"No supported files ({', '.join(supported_exts)}) found under: {src_dir} (skipping conversion)")
        return

    for src_path in candidates:
        try:
            rel = src_path.relative_to(src_dir)
            target = out_dir / rel.with_suffix(".md")
            target.parent.mkdir(parents=True, exist_ok=True)

            if skip_existing and target.exists():
                print(f"Skipped (exists): {src_path} -> {target}")
                continue

            result = md.convert(str(src_path))
            target.write_text(result.markdown, encoding="utf-8")
            print(f"Converted: {src_path} -> {target}")
        except Exception as e:
            print(f"Failed: {src_path} -> {e}")

def fetch_documents():
    folders = glob.glob(str(Path(KNOWLEDGE_BASE) / "*"))
    documents = []
    for folder in folders:
        doc_type = os.path.basename(folder)
        loader = DirectoryLoader(
            folder,
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8", "autodetect_encoding": False}
        )
        folder_docs = loader.load()
        for doc in folder_docs:
            doc.metadata["doc_type"] = doc_type
            src = doc.metadata.get("source") or ""
            doc.metadata["source_label"] = os.path.basename(src) if src else doc_type
            documents.append(doc)
    return documents

def create_chunks(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    return chunks

def create_embeddings_in_milvus(chunks):
    connection_args = {
        "host": MILVUS_HOST,
        "port": MILVUS_PORT,
        "user": MILVUS_USER,
        "password": MILVUS_PASSWORD,
        "db_name": MILVUS_DB_NAME,
        "secure": MILVUS_SECURE,
    }

    # HNSW index with IP metric matches runtime retrieval
    index_params = {
        "metric_type": "IP",
        "index_type": "HNSW",
        "params": {"M": 16, "efConstruction": 128}
    }
    search_params = {"metric_type": "IP", "params": {"ef": 64}}

    vectorstore = Milvus.from_documents(
        documents=chunks,
        embedding=embeddings,  # keep consistent with runtime
        connection_args=connection_args,
        collection_name=COLLECTION_NAME,
        index_params=index_params,
        search_params=search_params,
        drop_old=True
    )
    return vectorstore

if __name__ == "__main__":
    # Step 1: Convert supported files to Markdown
    convert_files_to_md(PDF_DIR, MD_DIR, skip_existing=True)

    # Step 2: Ingest Markdown files into vector DB
    documents = fetch_documents()
    if not documents:
        print(f"No Markdown files found under: {KNOWLEDGE_BASE}")
    else:
        chunks = create_chunks(documents)
        create_embeddings_in_milvus(chunks)
        print("Ingestion to Milvus is complete")