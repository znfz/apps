import os
import glob
import warnings
from pathlib import Path
from dotenv import load_dotenv
from markitdown import MarkItDown
import onnxruntime as ort

ort.set_default_logger_severity(4)  # 0=V,1=I,2=W,3=E,4=FATAL
so = ort.SessionOptions()
so.intra_op_num_threads = 1
so.inter_op_num_threads = 1

# Ingestion and embeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
PDF_DIR = REPO_ROOT / "files_pdf"
MD_DIR = REPO_ROOT / "files_md"
DB_NAME = str(REPO_ROOT / "vector_db")

# Model and embeddings
load_dotenv(override=True)
MODEL = "gpt-4.1-nano"  # kept for reference if used elsewhere
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")


def convert_pdfs_to_md(pdf_dir: Path = PDF_DIR, out_dir: Path = MD_DIR, skip_existing: bool = True) -> None:
    """
    Convert all PDFs under pdf_dir to Markdown under out_dir, preserving directory structure.
    Skips already converted files when skip_existing is True.
    """
    md = MarkItDown()

    if not pdf_dir.exists():
        print(f"PDF directory does not exist: {pdf_dir} (skipping conversion)")
        return

    pdf_files = sorted(pdf_dir.rglob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found under: {pdf_dir} (skipping conversion)")
        return

    for pdf_path in pdf_files:
        try:
            rel = pdf_path.relative_to(pdf_dir)
            target = out_dir / rel.with_suffix(".md")
            target.parent.mkdir(parents=True, exist_ok=True)

            if skip_existing and target.exists():
                print(f"Skipped (exists): {pdf_path} -> {target}")
                continue

            result = md.convert(str(pdf_path))
            target.write_text(result.markdown, encoding="utf-8")
            print(f"Converted: {pdf_path} -> {target}")
        except Exception as e:
            print(f"Failed: {pdf_path} -> {e}")


def fetch_documents():
    folders = glob.glob(str(Path(KNOWLEDGE_BASE) / "*"))
    documents = []
    for folder in folders:
        doc_type = os.path.basename(folder)
        loader = DirectoryLoader(
            folder,
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={'autodetect_encoding': True}
        )
        folder_docs = loader.load()
        for doc in folder_docs:
            doc.metadata["doc_type"] = doc_type
            documents.append(doc)
    return documents


def create_chunks(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    return chunks


def create_embeddings(chunks):
    if os.path.exists(DB_NAME):
        # Reset the existing collection before rebuilding
        Chroma(persist_directory=DB_NAME, embedding_function=embeddings).delete_collection()
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_NAME
    )
    return vectorstore


if __name__ == "__main__":
    # Step 1: Convert PDFs to Markdown (safe to run multiple times)
    convert_pdfs_to_md(PDF_DIR, MD_DIR, skip_existing=True)

    # Step 2: Ingest Markdown files into vector DB
    documents = fetch_documents()
    if not documents:
        print(f"No Markdown files found under: {KNOWLEDGE_BASE}")
    else:
        chunks = create_chunks(documents)
        create_embeddings(chunks)
        print("Ingestion is complete")
