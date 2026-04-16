# Vectara API Tutorial Series

This tutorial series provides a comprehensive, hands-on introduction to building RAG (Retrieval-Augmented Generation) applications using Vectara's REST API. Through ten progressive notebooks, you'll learn to create corpora, ingest data, query information, build intelligent AI agents, orchestrate multi-agent workflows, work with file artifacts, create data analysis tools with NumPy and Pandas, use reranker instructions for domain-specific relevance tuning, constrain agent output with JSON schemas and multi-step flows, and automate agents on cron or interval schedules.

## About Vectara

[Vectara](https://vectara.com/) is the Agent Platform for trusted enterprise AI: a unified Agentic RAG platform with built-in multi-modal retrieval, orchestration, and always-on governance. Deploy it on-prem (air-gapped), in your VPC, or as SaaS.

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
                {"type": "customer_reranker", "reranker_name": "qwen3-reranker", "limit": 30},
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
  - Stage 1: `qwen3-reranker` (multilingual, referenced by name) narrows to top 30
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

### [Notebook 5: Sub-Agents](5-sub-agents.ipynb)

**What you'll learn:**
- Create specialized sub-agents for domain-specific tasks
- Configure a parent orchestrator agent that delegates to sub-agents
- Understand session modes (ephemeral, persistent, llm_controlled)
- Build modular, reusable agent workflows

**What you'll build:**
A **Multi-Agent Research System** with:
1. **Research Paper Analyst**: Specialized in analyzing academic papers on RAG, embeddings, and retrieval
2. **Documentation Expert**: Expert at finding implementation guidance from Vectara docs
3. **Web Search Expert**: Finds current information and news from the internet
4. **AI Research Orchestrator**: Parent agent that delegates to the specialized sub-agents

**Sub-agent configuration:**
```python
orchestrator_config = {
    "name": "AI Research Orchestrator",
    "tool_configurations": {
        "research_analyst": {
            "type": "sub_agent",
            "description_template": "Delegate academic research analysis tasks...",
            "sub_agent_configuration": {
                "agent_key": research_analyst_key,
                "session_mode": "ephemeral"
            }
        },
        "docs_expert": {
            "type": "sub_agent",
            "sub_agent_configuration": {
                "agent_key": docs_expert_key,
                "session_mode": "ephemeral"
            }
        },
        "web_search_expert": {
            "type": "sub_agent",
            "sub_agent_configuration": {
                "agent_key": web_search_expert_key,
                "session_mode": "ephemeral"
            }
        }
    }
}
```

**Key concepts:**
- **Sub-agents**: Specialized agents that handle domain-specific tasks
- **Orchestration**: Parent agent analyzes requests and delegates to appropriate sub-agents
- **Session modes**: Control how sub-agent sessions are managed
  - `ephemeral`: Fresh session every time (no state leakage)
  - `persistent`: Reuse same session (accumulate knowledge)
  - `llm_controlled`: LLM decides whether to resume or create new
- **Context isolation**: Each sub-agent maintains its own conversation history
- **Parallel execution**: Run multiple sub-agents simultaneously for comprehensive answers

**Benefits of sub-agents:**
- Better performance through specialized, focused agents
- Reduced context window pressure
- Modular, reusable agent components
- Cleaner separation of concerns

---

### [Notebook 6: Artifacts](6-artifacts.ipynb)

**What you'll learn:**
- Upload files (PDFs, images, documents) to agent sessions
- List and retrieve artifact details
- Create agents with artifact-processing tools
- Have agents analyze uploaded files and generate new artifacts

**What you'll build:**
A **Document Analyst** agent that can:
- Read and analyze uploaded documents and images
- Search for patterns within artifact content
- Convert documents between formats
- Generate new artifacts (reports, summaries)

**Key concepts:**
- **Artifacts**: Session-specific files that enable agents to work with files on-the-fly
- **Artifact tools**: `artifact_read`, `image_read`, `document_conversion`, `artifact_grep`
- **Two-way flow**: Users upload files, agents can generate new artifacts
- **Session scope**: Artifacts persist within a session without permanent indexing

---

### [Notebook 7: Lambda Tools for Data Analysis](7-lambda-tools-data-analysis.ipynb)

**What you'll learn:**
- Create Lambda tools that use NumPy and Pandas for data analysis
- Pass structured data (JSON) to tools and receive computed results
- Build tools for statistical analysis, trend detection, and data transformation
- Combine multiple data analysis tools in agent workflows

**What you'll build:**
Two **Data Analysis Lambda Tools**:
1. **Statistical Analyzer**: Descriptive statistics, correlations, percentiles using Pandas
2. **Trend Analyzer**: Moving averages, growth rates, linear regression using NumPy

**Lambda tool configuration:**
```python
tool_config = {
    "type": "lambda",
    "language": "python",
    "name": "statistical_analyzer",
    "title": "Statistical Analyzer",
    "description": "Compute statistics on tabular data using Pandas...",
    "code": """
import json
import pandas as pd
import numpy as np

def process(data: str, columns: str = "", operations: str = "describe") -> dict:
    df = pd.DataFrame(json.loads(data))
    # ... compute statistics
    return {"success": True, "statistics": {...}}
"""
}
```

**Key concepts:**
- **Lambda tools execute real Python code** with NumPy and Pandas available
- **Data passed as JSON strings** between agents and tools
- **Precise numerical computation** that LLMs cannot reliably perform
- **Multi-tool workflows** for comprehensive data analysis

**Use cases:**
- Financial analysis and reporting
- Sales and marketing analytics
- Scientific data processing
- Time-series analysis

---

### [Notebook 8: Reranker Instructions](8-reranker-instructions.ipynb)

**What you'll learn:**
- Use reranker instructions with `qwen3-reranker` to guide relevance scoring
- Implement role-based intent steering to prioritize practical docs over academic papers
- Create domain-specific glossaries to resolve abbreviations and jargon
- Compare baseline reranking with instruction-guided reranking

**What you'll build:**
Three query examples demonstrating:
1. **Baseline**: `qwen3-reranker` without instructions across both corpora
2. **Role-based intent steering**: Instructions that prioritize practical Vectara docs for a developer audience
3. **Abbreviation resolution**: A glossary that helps the reranker understand "HHEM" means Hughes Hallucination Evaluation Model

**Key concepts:**
- **Reranker instructions**: A text parameter that provides domain context to guide the reranker's scoring
- **`reranker_name` vs `reranker_id`**: Reference a built-in reranker by name (`reranker_name: "qwen3-reranker"`) or a customer-specific one by ID (`reranker_id: "rnk_..."`) — the tutorials use `reranker_name` so they work out-of-the-box for any account
- **Intent steering**: Shift result rankings toward a specific user persona without changing the query
- **Jargon resolution**: Help the reranker bridge the gap between abbreviations in queries and full terms in documents

---

### [Notebook 9: Structured Output & Multi-Step Agents](9-structured-output-multi-step.ipynb)

**What you'll learn:**
- Constrain agent output to a JSON schema so responses are machine-parseable
- Define multi-step agents with a classifier step that routes to specialized handlers
- Use `next_steps` with JSONPath conditions (e.g. `get('$.output.intent')`) to drive branching
- Mix `structured` and `default` output parsers across steps

**What you'll build:**
1. **Research Entity Extractor**: Single-step agent that returns a JSON object with `topics`, `techniques`, `confidence`, etc. — schema-enforced
2. **Research Assistant Router**: Two-stage agent that classifies an incoming query (`research` / `implementation` / `comparison`) and routes to the matching handler step

**Key concepts:**
- **Structured output**: `output_parser: {"type": "structured", "schema": {...}, "strict": True}` guarantees valid JSON matching the declared schema
- **Multi-step agents**: Define named steps under `steps` and declare a `first_step_name`; each step can have its own tools, instructions, and parser
- **Conditional routing**: Use `next_steps` with JSONPath conditions on the prior step's structured output
- **Scoped tools**: `allowed_tools: []` on a classifier step prevents tool calls during classification

---

### [Notebook 10: Agent Schedules](10-agent-schedules.ipynb)

**What you'll learn:**
- Automate agent execution with cron-based and interval-based schedules
- Enable, update, and delete schedules via the REST API
- Inspect execution history and the sessions created by scheduled runs

**What you'll build:**
A **Research Digest Generator** agent with two schedules:
1. **Daily Research Digest**: Cron schedule `0 9 * * 1-5` (weekdays at 9 AM UTC)
2. **Periodic Research Check**: Interval schedule `PT6H` (every 6 hours, ISO-8601)

**Key concepts:**
- **Cron vs. interval**: Use cron for wall-clock cadence (business hours, specific days); use interval for "every N hours" regardless of start time
- **`enabled: false`**: Create schedules disabled during development and enable them once you're happy with the config
- **`max_executions_to_keep`**: Cap retained execution history per schedule to control storage
- **Sessions are created automatically** for each run, so you can inspect the agent's events/output for any scheduled execution

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

5. Sub-Agents
   ↓
   Create multi-agent workflows with specialized sub-agents

6. Artifacts
   ↓
   Work with files in agent sessions

7. Lambda Tools for Data Analysis
   ↓
   Build NumPy/Pandas-powered data analysis tools

8. Reranker Instructions
   ↓
   Guide relevance scoring with domain-specific instructions

9. Structured Output & Multi-Step Agents
   ↓
   Constrain agent output to JSON schemas; route queries through multi-step flows

10. Agent Schedules
    ↓
    Automate agent runs on cron or interval schedules
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
3. **Agent reuse** - Notebooks 4 and 5 check if agents already exist before creating duplicates
4. **Rate limiting** - The notebooks include small delays between API calls to be respectful
5. **Cleanup** - Consider deleting test corpora/agents when done to keep your account organized
6. **Sub-agent dependencies** - Notebook 5 creates sub-agents first, then a parent orchestrator that references them

## Key API Endpoints Used

| Endpoint | Purpose | Notebook |
|----------|---------|----------|
| `POST /v2/corpora` | Create corpus | 1 |
| `GET /v2/corpora` | List corpora | 1 |
| `POST /v2/corpora/{key}/upload_file` | Upload files | 2 |
| `POST /v2/corpora/{key}/documents` | Index documents | 2 |
| `GET /v2/corpora/{key}/documents` | List documents | 2 |
| `POST /v2/query` | Query corpora | 3, 8 |
| `POST /v2/agents` | Create agent | 4, 5, 6, 7, 9, 10 |
| `POST /v2/agents/{key}/sessions` | Create session | 4, 5, 6, 7, 9 |
| `POST /v2/agents/{key}/sessions/{key}/events` | Send messages / Upload artifacts | 4, 5, 6, 7, 9 |
| `GET /v2/agents/{key}/sessions/{key}/events` | Get conversation history | 4, 10 |
| `GET /v2/agents/{key}/sessions/{key}/artifacts` | List session artifacts | 6 |
| `GET /v2/agents` | List agents | 5, 9, 10 |
| `DELETE /v2/agents/{key}` | Delete agent | 5, 6, 7, 9, 10 |
| `POST /v2/tools` | Create Lambda tool | 5, 7 |
| `GET /v2/tools` | List Lambda tools | 5, 7 |
| `DELETE /v2/tools/{id}` | Delete Lambda tool | 5, 7 |
| `POST /v2/agents/{key}/schedules` | Create schedule | 10 |
| `GET /v2/agents/{key}/schedules` | List schedules | 10 |
| `PATCH /v2/agents/{key}/schedules/{key}` | Update schedule | 10 |
| `DELETE /v2/agents/{key}/schedules/{key}` | Delete schedule | 10 |
| `GET /v2/agents/{key}/schedules/{key}/executions` | Execution history | 10 |

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
