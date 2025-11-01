# Vectara API Tutorial Series

This tutorial series provides a comprehensive, hands-on introduction to building RAG (Retrieval-Augmented Generation) applications using Vectara's REST API. Through four progressive notebooks, you'll learn to create corpora, ingest data, query information, and build intelligent AI agents.

## About Vectara

[Vectara](https://vectara.com/) is the Agent Operating System for trusted enterprise AI: a unified Agentic RAG platform with built-in multi-modal retrieval, orchestration, and always-on governance. Deploy it on-prem (air-gapped), in your VPC, or as SaaS.

Key features:
- **Simple Integration**: RESTful APIs and SDKs for Python, TypeScript, and Java
- **Flexible Deployment**: SaaS, VPC, or on-premises options
- **Multi-Modal Support**: Index and search across text, tables, and images
- **Advanced Retrieval**: Hybrid search with semantic and keyword matching plus reranking
- **Grounded Generation**: LLM responses with citations and factual consistency scores
- **Enterprise-Ready**: Built-in access controls, audit logging, and compliance (SOC2, HIPAA)

## Prerequisites

Before starting, you'll need:
1. A Vectara account - [Sign up here](https://console.vectara.com/signup)
2. A personal API key from the Vectara console
3. Set your API key as an environment variable: `export VECTARA_API_KEY='your-api-key'`

## Tutorial Overview

### [Notebook 1: Corpus Creation](1-corpus-creation.ipynb)

**What you'll learn:**
- Create corpora using Vectara's REST API
- Configure embedding models (Boomerang)
- Define filterable attributes for metadata-based search
- Verify corpus creation and list existing corpora

**What you'll build:**
Two corpora with different purposes:
1. **AI Research Papers**: For academic papers from ArXiv about RAG, LLMs, and retrieval
   - Filter attributes: `source`, `year`, `topic`
2. **Vectara Documentation**: For Vectara product documentation and guides
   - Filter attributes: `source`, `doc_type`, `topic`

**Key concepts:**
- Corpora are containers for your documents
- Each corpus has a unique key for identification
- Embedding models (like Boomerang) convert text to semantic vectors
- Filter attributes enable metadata-based filtering during queries

---

### [Notebook 2: Data Ingestion](2-data-ingestion.ipynb)

**What you'll learn:**
- Upload files (PDFs) using the File Upload API
- Index structured data using the Core Indexing API
- Build a web crawler to extract documentation
- Verify successful ingestion

**What you'll build:**
1. **Upload Research Papers**: Download and upload 7 AI research papers from ArXiv
   - Papers include seminal works on GPT-3, RAG, Transformers, BEIR benchmark, etc.
   - Vectara automatically extracts text, chunks content, and creates embeddings

2. **Crawl and Index Documentation**: Build a custom web crawler that:
   - Crawls docs.vectara.com (50 pages)
   - Extracts meaningful content and creates chunks
   - Automatically categorizes by doc_type and topic
   - Indexes 41 documentation pages with 1000+ chunks

**Key concepts:**
- **File Upload API**: Best for PDFs, documents, and binary files - Vectara handles chunking
- **Core Indexing API**: Best for pre-chunked text or structured data you control
- **Chunking**: Breaking documents into smaller pieces for better retrieval
- **Metadata**: Attach custom attributes for filtering and organization

**Data ingested:**
- 7 research papers (PDF format)
- 41 documentation pages (pre-chunked text)
- Total: 48 documents across both corpora

---

### [Notebook 3: Query API](3-query-api.ipynb)

**What you'll learn:**
- Execute basic queries with hybrid search
- Configure reranking for better relevance
- Query multiple corpora simultaneously
- Apply metadata filters to narrow results
- Stream responses for real-time UX
- Understand citations and factual consistency scores

**Examples covered:**

#### Example 1: Basic Query with Hybrid Search
```python
query_request = {
    "query": "What is retrieval augmented generation?",
    "search": {
        "corpora": [{"corpus_key": research_corpus_key, "lexical_interpolation": 0.005}],
        "limit": 100,
        "reranker": {
            "type": "chain",
            "rerankers": [
                {"type": "customer_reranker", "reranker_id": "rnk_272725719", "limit": 30},
                {"type": "mmr", "diversity_bias": 0.05}
            ]
        }
    },
    "generation": {
        "generation_preset_name": "vectara-summary-ext-24-05-med-omni",
        "max_used_search_results": 10,
        "enable_factual_consistency_score": True
    }
}
```

**Key concepts:**
- **Hybrid search**: Combines semantic and keyword matching (lexical_interpolation parameter)
- **Chain reranker**: Two-stage reranking for optimal relevance and diversity
  - Stage 1: Customer reranker (multilingual) narrows to top 30
  - Stage 2: MMR reranker adds diversity, returns top 10
- **Factual Consistency Score (FCS)**: Detects potential hallucinations (0.0-1.0 scale)

#### Example 2: Multi-Corpus Queries
Query across both research papers AND documentation simultaneously to combine theoretical insights with practical implementation guidance.

#### Example 3: Metadata Filtering
Filter results by year, topic, or doc_type:
```python
"metadata_filter": "doc.year >= 2023"
```

#### Example 4: Streaming Responses
Stream generated responses in real-time using Server-Sent Events for better UX.

---

### [Notebook 4: Agent API](4-agent-api.ipynb)

**What you'll learn:**
- Create AI agents with custom instructions
- Configure tool access for agents
- Create and manage conversation sessions
- Send messages and maintain multi-turn context
- View conversation history

**What you'll build:**
A **RAG Research Assistant** agent that:
- Has access to both research papers and documentation corpora
- Uses GPT-4o for reasoning and generation
- Can autonomously search both corpora using tool configurations
- Maintains conversation context across multiple turns
- Combines theoretical research insights with practical implementation guidance

**Agent configuration:**
```python
agent_config = {
    "name": "RAG Research Assistant",
    "model": {"name": "gpt-4o"},
    "first_step": {
        "type": "conversational",
        "instructions": [...],  # Custom system prompt
        "output_parser": {"type": "default"}
    },
    "tool_configurations": {
        "research_paper_search": {
            "type": "corpora_search",
            "query_configuration": {...}  # Search research corpus
        },
        "vectara_doc_search": {
            "type": "corpora_search",
            "query_configuration": {...}  # Search docs corpus
        }
    }
}
```

**Key concepts:**
- **Agents vs Queries**: Agents orchestrate multiple queries, maintain context, and reason across turns
- **Sessions**: Conversations with state and history
- **Tools**: Functions agents can call (like corpora search)
- **Multi-turn conversations**: Agent remembers previous context

**Example interaction:**
```
User: "What is hybrid search?"
Agent: [Explains hybrid search using retrieved context]

User: "What are its main benefits?"
Agent: [Remembers we're discussing hybrid search, provides benefits]

User: "Can you give me an example?"
Agent: [Provides concrete example while maintaining context]
```

---

## Tutorial Flow

```
1. Corpus Creation
   ↓
   Create two corpora with metadata attributes

2. Data Ingestion
   ↓
   Upload PDFs + Index crawled documentation

3. Query API
   ↓
   Search, filter, rerank, and generate answers

4. Agent API
   ↓
   Build autonomous agents with tools and context
```

## Running the Notebooks

### Option 1: Google Colab
Click the "Open in Colab" badge at the top of each notebook to run in your browser without setup.

### Option 2: Local Jupyter
```bash
# Clone the repository
git clone https://github.com/vectara/example-notebooks.git
cd example-notebooks/notebooks/api-examples

# Install dependencies
pip install requests beautifulsoup4

# Set your API key
export VECTARA_API_KEY='your-api-key-here'

# Launch Jupyter
jupyter notebook
```

## Important Notes

1. **Run notebooks in order** - Each notebook builds on the previous one
2. **Corpus keys** - Save the corpus keys from Notebook 1, you'll need them in subsequent notebooks
3. **Agent reuse** - Notebook 4 checks if agents already exist before creating duplicates
4. **Rate limiting** - The notebooks include small delays between API calls to be respectful
5. **Cleanup** - Consider deleting test corpora/agents when done to keep your account organized

## Key API Endpoints Used

| Endpoint | Purpose | Notebook |
|----------|---------|----------|
| `POST /v2/corpora` | Create corpus | 1 |
| `GET /v2/corpora` | List corpora | 1 |
| `POST /v2/corpora/{key}/upload_file` | Upload files | 2 |
| `POST /v2/corpora/{key}/documents` | Index documents | 2 |
| `GET /v2/corpora/{key}/documents` | List documents | 2 |
| `POST /v2/query` | Query corpora | 3 |
| `POST /v2/agents` | Create agent | 4 |
| `POST /v2/agents/{key}/sessions` | Create session | 4 |
| `POST /v2/agents/{key}/sessions/{key}/events` | Send messages | 4 |
| `GET /v2/agents/{key}/sessions/{key}/events` | Get conversation history | 4 |

## Additional Resources

- [Vectara Documentation](https://docs.vectara.com/)
- [API Reference](https://docs.vectara.com/docs/rest-api)
- [Python SDK](https://github.com/vectara/python-sdk)
- [Community Forum](https://discuss.vectara.com/)
- [Example Applications](https://github.com/vectara/vectara-examples)

## Support

For questions or issues:
- GitHub Issues: [example-notebooks/issues](https://github.com/vectara/example-notebooks/issues)
- Community Forum: [discuss.vectara.com](https://discuss.vectara.com/)
- Documentation: [docs.vectara.com](https://docs.vectara.com/)

## License

These notebooks are provided as examples under the Apache 2.0 License.
