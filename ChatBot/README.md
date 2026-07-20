# RAG Chatbot Assistant

A Retrieval-Augmented Generation (RAG) chatbot application for querying document knowledge bases through natural language.

## Overview

This RAG chatbot enables users to query a knowledge base of technical documents through a conversational interface. The application uses advanced RAG techniques to provide accurate, context-based answers with source citations from your document collection.

## Key Features

- **Document Processing**: Converts PDF, DOCX, and PPTX files to Markdown
- **Intelligent Retrieval**: MMR (Maximal Marginal Relevance) algorithm for diverse, relevant results
- **Dynamic K-Selection**: Automatically adjusts retrieval based on query complexity
- **Query Expansion & Rewriting**: Acronym expansion, synonym addition, and LLM-based reformulation
- **Streaming Responses**: Real-time token-by-token answer generation
- **Source Citations**: Every answer includes references to source documents
- **Context-Only Answers**: Only responds based on retrieved documents (no hallucinations)
- **Conversation History**: Maintains context across multiple questions
- **Interactive UI**: Clean Streamlit interface with Q&A layout
- **Confidence Scoring**: Quality metrics for each answer

## Technology Stack

- **Frontend**: Streamlit
- **LLM**: Azure OpenAI GPT models (configurable)
- **Embeddings**: Azure OpenAI `text-embedding-3-large`
- **Vector Database**: Milvus
- **Document Processing**: MarkItDown
- **Framework**: LangChain

## Quick Start

### Prerequisites

- Python 3.11+
- Azure OpenAI API access (or OpenAI API)
- Milvus server (local or remote)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/rag-chatbot.git
cd rag-chatbot
```

2. **Set up environment**:
```bash
conda create -n chat python=3.11 -y
conda activate chat
pip install -r requirements.txt
```

3. **Configure environment variables** (create `.env` file):
```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=<your_azure_openai_api_key>
AZURE_OPENAI_ENDPOINT=<your_azure_openai_endpoint>
AZURE_OPENAI_API_VERSION=2024-08-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=<your_deployment_name>
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=<your_embedding_deployment_name>

# Milvus Configuration
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION=files_md_embeddings
MILVUS_DB_NAME=default
MILVUS_SECURE=false

# Optional: Custom SSL Certificate
SSL_CERT_FILE=<path_to_ca_bundle>
```

**Note**: You can also use standard OpenAI API by modifying the configuration in `utils/answer.py` and `utils/ingest.py`.

4. **Set up Milvus** (if running locally):
```bash
# Using Docker
docker-compose up -d
# or follow Milvus installation guide: https://milvus.io/docs/install_standalone-docker.md
```

5. **Add documents**:
   - Place PDF, DOCX, or PPTX files in `files_original/`
   - Organize in subdirectories by category

6. **Run ingestion**:
```bash
python utils/ingest.py
```
This converts documents to Markdown, generates embeddings, and stores them in Milvus.

7. **Launch the app**:
```bash
python app.py
# or
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## Usage

1. Type your question in the chat input at the bottom
2. Questions appear on the right (Q1, Q2, etc.)
3. Answers stream on the left with sources
4. Click expandable source sections to see full document content
5. Use sidebar to:
   - Re-ask recent questions
   - Download conversation history
   - Clear conversation

## Project Structure

```
chatbot/
├── app.py                    # Streamlit UI
├── requirements.txt          # Dependencies
├── .env                      # Configuration
├── files_original/           # Source documents (PDF, DOCX, PPTX)
├── files_md/                 # Converted Markdown files
└── utils/
    ├── ingest.py            # Document processing & embedding
    └── answer.py            # Retrieval & LLM logic
```

## Configuration

### Retrieval Parameters (utils/answer.py)

**Dynamic K-Selection (Automatic)**:
The system automatically adjusts retrieval parameters based on query type:

| Query Type | k (docs) | fetch_k | Example |
|------------|----------|---------|---------|
| Simple Factual | 5 | 40 | "What is lyophilization?" |
| Moderate | 8 | 60 | Standard questions |
| Comparison | 10 | 80 | "Compare method A vs B" |
| Procedural | 12 | 90 | "Steps for stability testing" |
| Analytical | 12 | 90 | "Why does pH affect stability?" |

**Base Configuration**:
```python
BASE_K = 8               # Default for moderate queries
BASE_FETCH_K = 60        # Default candidate pool
LAMBDA_MULT = 0.5        # Similarity/diversity balance (0-1)
```

See [DYNAMIC_K_SELECTION.md](DYNAMIC_K_SELECTION.md) for detailed documentation.

**Query Expansion & Rewriting**:
Automatically enhances queries before retrieval:

| Feature | Example | Benefit |
|---------|---------|---------|
| Acronym Expansion | "API" → "API (Active Pharmaceutical Ingredient)" | Matches documents using full terminology |
| Synonym Addition | "stability" → adds "shelf life, storage" | Captures alternative phrasing |
| LLM Reformulation | "How is it tested?" → "What are testing methods for protein aggregation?" | Adds missing context from conversation |

Configuration:
```bash
# .env file
ENABLE_QUERY_EXPANSION=true
ENABLE_LLM_REWRITING=true
```

See [QUERY_EXPANSION.md](QUERY_EXPANSION.md) for detailed documentation.

### Chunking Parameters (utils/ingest.py)

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # Characters per chunk
    chunk_overlap=200    # Overlap for continuity
)
```

### LLM Model (utils/answer.py)

```python
MODEL = "gpt-4"  # Change to gpt-4o, gpt-4-turbo, gpt-35-turbo, etc.
```

## Deployment

This application can be deployed to various platforms:

### Docker Deployment

```bash
# Build Docker image
docker build -t rag-chatbot .

# Run container
docker run -p 8501:8501 --env-file .env rag-chatbot
```

### Cloud Platforms

The app can be deployed to:
- **Streamlit Cloud**: Direct GitHub integration
- **Heroku**: Using Procfile configuration
- **AWS/Azure/GCP**: Deploy as containerized application
- **Any server**: Run with `streamlit run app.py`

### Deployment Checklist

**Before Deployment**:
- [ ] Test app locally: `streamlit run app.py`
- [ ] Verify Milvus connection and embeddings exist
- [ ] Ensure requirements.txt is up to date
- [ ] Secure environment variables (use secrets management)
- [ ] Verify no sensitive data in code

**After Deployment**:
- [ ] Test a sample query
- [ ] Check environment variables are configured
- [ ] Verify source document retrieval works
- [ ] Monitor application logs

## How It Works

1. **Document Ingestion**:
   - Converts documents to Markdown using MarkItDown
   - Splits text into chunks (500 chars, 200 overlap)
   - Generates embeddings via Azure OpenAI
   - Stores vectors in Milvus with HNSW indexing

2. **Query Processing**:
   - Expands pharmaceutical acronyms (58 acronyms: API, mAb, ICH, CMC, etc.)
   - Adds domain-specific synonyms (formulation, stability, lyophilization, etc.)
   - Reformulates vague queries using LLM and conversation context
   - Analyzes query complexity and type (factual, comparison, procedural, analytical)
   - Dynamically adjusts k and fetch_k parameters
   - Combines user question with conversation history
   - Retrieves top-k relevant chunks using MMR
   - Constructs prompt with retrieved context
   - Streams LLM response token-by-token

3. **Answer Generation**:
   - System prompt enforces context-only answering
   - If no relevant context, responds: "I don't have information about that in my knowledge base"
   - Includes source document references

## Maintenance

### Adding New Documents

1. Place files in `files_original/` (maintain folder structure)
2. Run `python utils/ingest.py`
3. Restart the app

### Updating Documents

1. Delete corresponding `.md` file in `files_md/`
2. Update source file in `files_original/`
3. Run `python utils/ingest.py`

### Monitoring

- Check Milvus connection status
- Monitor Azure OpenAI API usage and rate limits
- Review Streamlit logs for errors

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Milvus connection errors | Verify `MILVUS_HOST`, `MILVUS_PORT` in `.env` |
| SSL certificate errors | Set `SSL_CERT_FILE` to your CA bundle path |
| Empty responses | Check if collection exists and has documents |
| Slow retrieval | Increase `ef` parameter or reduce `fetch_k` |
| Poor answer quality | Adjust `chunk_size`, increase `k`, or tune system prompt |
| Answers outside context | Verify strict system prompt in `utils/answer.py` |

## Key Design Decisions

**Why Milvus?**
- High-performance vector search
- HNSW indexing for fast nearest neighbor retrieval
- Excellent LangChain integration

**Why MMR Retrieval?**
- Reduces redundancy in retrieved chunks
- Balances relevance with diversity
- Ensures comprehensive coverage

**Why Streaming?**
- Better user experience
- Lower perceived latency
- Immediate feedback

**Why Context-Only Answers?**
- Prevents hallucinations
- Ensures factual accuracy
- Limits scope to curated documents

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Built with [LangChain](https://github.com/langchain-ai/langchain)
- Vector database powered by [Milvus](https://milvus.io/)
- UI built with [Streamlit](https://streamlit.io/)
- Document processing via [MarkItDown](https://github.com/microsoft/markitdown)
