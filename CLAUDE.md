# DPDT Assistant - RAG Chatbot

## Project Overview

DPDT Assistant is a Retrieval-Augmented Generation (RAG) chatbot application designed for the Drug Product Development and Technology (DPDT) group at Regeneron. The application enables users to query a knowledge base of technical documents through a conversational interface, providing accurate answers with relevant context from the document collection.

## Architecture

### Technology Stack

- **Frontend**: Streamlit - Web-based chat interface with two-column layout
- **LLM**: GPT-4.1-nano via Regeneron AIR API (Azure-compatible endpoint)
- **Embeddings**: Azure OpenAI `text-embed-3-large` via Regeneron AIR API
- **Vector Database**: Milvus (standalone or cluster)
- **Document Processing**: MarkItDown for PDF/DOCX/PPTX to Markdown conversion
- **Framework**: LangChain for RAG orchestration
- **Deployment**: RStudio Connect (rsconnect-python)

### Core Components

1. **app.py** - Main Streamlit application
   - Streaming chat interface with Q&A interleaved layout
   - Expandable source document display with full paths
   - Two-column layout (left: answers + sources, right: questions)
   - Conversation download and clear functionality
   - Recently asked questions sidebar

2. **utils/ingest.py** - Document ingestion pipeline
   - Converts documents to Markdown (preserves directory structure)
   - Chunks text with overlap (500 chars, 200 overlap)
   - Generates embeddings via Azure OpenAI
   - Stores in Milvus with HNSW indexing

3. **utils/answer.py** - Query processing and retrieval
   - MMR (Maximal Marginal Relevance) retrieval strategy
   - Conversation history-aware querying
   - Streaming response generation
   - **Strict context-only answering**: Only responds based on retrieved documents
   - Custom SSL context handling for Regeneron certificates

## Data Flow

```
Documents (PDF/DOCX/PPTX)
    ↓
MarkItDown Conversion
    ↓
Markdown Files (files_md/)
    ↓
Text Chunking (RecursiveCharacterTextSplitter)
    ↓
Azure OpenAI Embeddings (text-embedding-3-large)
    ↓
Milvus Vector Store (HNSW index, IP metric)
    ↓
User Query → MMR Retrieval (k=8, fetch_k=60)
    ↓
Context + History → GPT-4.1-nano
    ↓
Streaming Response + Source Documents
```

## Directory Structure

```
chatbot/
├── app.py                    # Streamlit UI application
├── run.sh                    # Conda environment launcher
├── requirements.txt          # Python dependencies
├── .env                      # Environment configuration
├── README.md                 # User documentation
├── CLAUDE.md                 # This file (project documentation)
├── files_original/           # Source documents (PDF, DOCX, PPTX)
├── files_md/                 # Converted Markdown files
│   ├── Best Practices/
│   ├── Developability Assessment/
│   └── Technical Reports/
└── utils/
    ├── ingest.py            # Document processing & embedding
    ├── answer.py            # Retrieval & LLM logic
    └── auth.py              # Authentication utilities (if needed)
```

## Key Features

### Document Processing
- **Multi-format support**: PDF, DOCX, DOC, PPTX, PPT
- **Automatic conversion**: MarkItDown converts all documents to Markdown
- **Directory preservation**: Maintains folder structure from source to Markdown
- **Skip existing**: Avoids re-converting already processed files

### Intelligent Retrieval
- **MMR algorithm**: Balances relevance and diversity in retrieved chunks
- **Conversation-aware**: Combines current question with conversation history
- **Configurable parameters**:
  - k=8: Final number of documents returned
  - fetch_k=60: Candidate pool size
  - lambda_mult=0.5: Similarity/diversity balance

### Vector Database Configuration
- **Index**: HNSW (Hierarchical Navigable Small World)
  - M=16: Number of bi-directional links
  - efConstruction=128: Build-time search depth
  - ef=64: Query-time search depth
- **Metric**: IP (Inner Product) for cosine-like similarity
- **Collection**: Configurable via MILVUS_COLLECTION env var

### User Interface
- **Streaming responses**: Real-time token-by-token output with loading spinner
- **Context display**: Expandable source documents with full file paths
- **Source tracking**: Each answer includes numbered source references
- **Conversation history**: Maintains context across multiple turns in session state
- **Q&A layout**: Interleaved question-answer format (Q1→A1→Q2→A2)
- **Download feature**: Export full conversation with sources to text file
- **Recently asked**: Sidebar shows last 5 questions for quick re-asking
- **Strict answering**: Only provides answers based on retrieved context

## Configuration

### Environment Variables (.env)

```bash
# Regeneron AIR API Authentication (required for both ingestion and runtime)
ACCESS_TOKEN=<regeneron_access_token>

# Milvus Connection
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_USER=
MILVUS_PASSWORD=
MILVUS_DB_NAME=default
MILVUS_SECURE=false
MILVUS_COLLECTION=files_md_embeddings

# SSL Certificate (optional, for custom CA bundle)
SSL_CERT_FILE=<path_to_ca_bundle>
# or
REQUESTS_CA_BUNDLE=<path_to_ca_bundle>
```

### Embedding Configuration

The application uses **unified embedding via Regeneron's AIR API**:

- **Both Ingestion & Runtime**: Azure OpenAI via Regeneron's AIR API
  - Endpoint: `https://air-api.regeneron.com/v1.0/model`
  - Model: `text-embed-3-large`
  - Authentication: Custom `authorization-token` header with ACCESS_TOKEN
  - API Version: `2024-08-01-preview`

**Note**: Both ingest.py and answer.py use the same AIR API endpoint and model, ensuring vector compatibility.

## Setup & Usage

### Prerequisites
- Python 3.11+
- Conda (for environment management)
- Access to Regeneron's AIR API with valid ACCESS_TOKEN
- Milvus server (local or remote)
- rsconnect-python (for deployment to RStudio Connect)

### Installation

1. Create and activate Conda environment:
```bash
conda create -n chat python=3.11 -y
conda activate chat
pip install -r requirements.txt
```

2. Configure environment variables in `.env`

3. Add source documents to `files_original/` (organized by category)

4. Run ingestion pipeline:
```bash
python utils/ingest.py
```

5. Launch the application:
```bash
bash run.sh
# or directly: python app.py
```

### Document Ingestion Workflow

1. Place documents in `files_original/` with subdirectories for organization
2. Run `python utils/ingest.py`:
   - Converts all supported files to Markdown in `files_md/`
   - Loads all `.md` files from subdirectories
   - Adds `doc_type` metadata based on folder name
   - Splits into 500-character chunks with 200-character overlap
   - Generates embeddings via Azure OpenAI
   - Stores in Milvus collection (drops old data)

### Querying the Assistant

1. Launch the app: `python app.py` or `streamlit run app.py`
2. Type questions in the chat input at the bottom
3. Questions appear on the right side (Q1, Q2, etc.)
4. Answers stream on the left side with source documents
5. Expand source documents to see full content and file paths
6. Use sidebar to re-ask recent questions or download conversation
7. Conversation history is preserved for follow-up questions within the session

### Deployment to RStudio Connect

Deploy the app to Regeneron's RStudio Connect:

```bash
rsconnect deploy streamlit \
  --server https://rnpd-connect.regeneron.regn.com \
  --api-key <your_api_key> \
  --entrypoint app.py \
  ./ \
  --insecure
```

## Technical Decisions

### Why Milvus?
- High-performance vector similarity search
- HNSW indexing for fast approximate nearest neighbor
- Support for various distance metrics
- Easy integration with LangChain

### Why MMR Retrieval?
- Reduces redundancy in retrieved chunks
- Ensures diverse perspectives from the knowledge base
- Balances relevance with coverage

### Why Streaming?
- Better user experience for long responses
- Immediate feedback while LLM generates
- Lower perceived latency

### Why Markdown Conversion?
- Uniform text format for all document types
- Cleaner text extraction than raw PDF parsing
- Preserves structure (headings, lists, tables)
- Human-readable intermediate format

## Customization Points

### Adjusting Chunk Size (ingest.py:108)
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # Increase for more context per chunk
    chunk_overlap=200    # Increase to preserve more continuity
)
```

### Tuning Retrieval (answer.py:68-74)
```python
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 8,              # Number of final documents
        "fetch_k": 60,       # Candidate pool (larger = more diverse)
        "lambda_mult": 0.5   # 0=diversity, 1=similarity
    }
)
```

### Changing LLM Model (answer.py:24)
```python
MODEL = "gpt-4.1-nano"  # Change to gpt-4o, gpt-4-turbo, etc.
```

### Modifying System Prompt (answer.py:40-51)
The system prompt enforces **strict context-only answering**. The assistant will:
- Only answer questions using information from retrieved documents
- Refuse to answer questions outside the knowledge base
- Explicitly state when information is not available

To customize the assistant's behavior, edit the SYSTEM_PROMPT variable.

## Known Limitations

1. **No authentication**: Streamlit interface requires external authentication (e.g., via RStudio Connect)

2. **No conversation persistence**: Session history resets on app restart or page refresh

3. **Fixed context window**: Always retrieves k=8 chunks regardless of query complexity

4. **No document versioning**: Re-ingestion drops old collection entirely

5. **Strict SSL requirements**: May require custom CA bundle configuration for Regeneron network

6. **Context-only responses**: Will not answer questions outside the document knowledge base (by design)

## Future Enhancements

- User authentication and session management (via RStudio Connect or LDAP)
- Conversation history persistence (database or file storage)
- Dynamic k-selection based on query complexity
- Document versioning and incremental updates
- Multi-tenancy support (user-specific collections)
- Advanced metadata filtering (date range, document type, category)
- Citation links to exact page numbers in source documents
- Admin interface for monitoring usage and performance
- Confidence scores for answers based on retrieval quality
- Feedback mechanism for answer quality improvement

## Maintenance

### Adding New Documents
1. Place files in `files_original/` (maintain subdirectory structure)
2. Run `python utils/ingest.py` (automatically skips existing conversions)
3. Restart app to ensure latest collection is loaded

### Updating Existing Documents
1. Delete corresponding `.md` file in `files_md/`
2. Update source file in `files_original/`
3. Run `python utils/ingest.py` to re-convert
4. Re-run ingestion to update embeddings

### Monitoring
- Check Milvus logs for connection issues
- Monitor Regeneron AIR API usage and rate limits
- Review Streamlit logs for user queries and errors
- Monitor RStudio Connect deployment status and logs

## Troubleshooting

**Milvus connection errors**: Verify host, port, and credentials in `.env`

**Embedding dimension mismatch**: Ensure both ingest.py and answer.py use same model

**Empty responses**: Check if collection exists and has documents (`MILVUS_COLLECTION`)

**Slow retrieval**: Increase `ef` parameter in search_params or reduce `fetch_k`

**Poor answer quality**: Adjust chunk_size, increase k, or modify system prompt

**SSL certificate errors**: Set SSL_CERT_FILE or REQUESTS_CA_BUNDLE environment variable to your CA bundle path

**Assistant answering outside context**: Verify system prompt in answer.py enforces strict context-only responses