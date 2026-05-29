# Vectara API Tutorial Series

This tutorial series provides a comprehensive, hands-on introduction to building RAG (Retrieval-Augmented Generation) applications using Vectara's REST API. Through fourteen progressive notebooks, you'll learn to create corpora, ingest data, delete documents, query information, build intelligent AI agents, orchestrate multi-agent workflows, work with file artifacts, create data analysis tools with NumPy and Pandas, use reranker instructions for domain-specific relevance tuning, constrain agent output with JSON schemas and multi-step flows, automate agents on cron or interval schedules, let agents call any REST API — public or authenticated, read or write — with the `web_get` tool, use **agent skills** to load specialist instructions on demand, and drive an agent through deterministic multi-phase pipelines using **agent steps**.

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

### [Notebook 3: Deleting Documents](3-document-deletion.ipynb)

**What you'll learn:**
- Delete a single document by its ID
- Bulk delete documents by metadata filter (`metadata_filter`) or by a list of document IDs
- Delete all documents at once by resetting a corpus
- List documents (optionally filtered by metadata) to verify deletions

**What you'll build:**
A self-contained walkthrough on its own `tutorial-document-deletion` corpus:
1. Create the corpus and add six small documents (four with `category`/`year` metadata, two without)
2. Delete one document by ID
3. Bulk delete every `finance` document with a metadata filter
4. Reset the corpus to remove everything, then optionally delete the corpus

**Key concepts:**
- **Single-document delete**: `DELETE /v2/corpora/{corpus_key}/documents/{document_id}`
- **Bulk delete**: `DELETE /v2/corpora/{corpus_key}/documents` with `metadata_filter` and/or `document_ids` (async by default; pass `async=false` to wait for results)
- **Corpus reset**: `POST /v2/corpora/{corpus_key}/reset` empties a corpus but keeps its configuration
- **Self-contained**: creates and owns its corpus, so it needs only a `VECTARA_API_KEY` and doesn't affect the other notebooks

---

### [Notebook 4: Query API](4-query-api.ipynb)

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

### [Notebook 5: Agent API](5-agent-api.ipynb)

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

### [Notebook 6: Sub-Agents](6-sub-agents.ipynb)

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

### [Notebook 7: Artifacts](7-artifacts.ipynb)

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

### [Notebook 8: Lambda Tools for Data Analysis](8-lambda-tools-data-analysis.ipynb)

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

### [Notebook 9: Reranker Instructions](9-reranker-instructions.ipynb)

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

### [Notebook 10: Structured Output & Multi-Step Agents](10-structured-output-multi-step.ipynb)

**What you'll learn:**
- Constrain agent output to a JSON schema so responses are machine-parseable
- Define multi-step agents with a classifier step that routes to specialized handlers
- Use `next_steps` with JSONPath conditions (e.g. `get('$.output.intent')`) to drive branching
- Mix `structured` and `default` output parsers across steps

**What you'll build:**
1. **Research Entity Extractor**: Single-step agent that returns a JSON object with `topics`, `techniques`, `confidence`, etc. — schema-enforced
2. **Research Assistant Router**: Two-stage agent that classifies an incoming query (`research` / `implementation` / `comparison`) and routes to the matching handler step

**Key concepts:**
- **Structured output**: `output_parser: {"type": "structured", "json_schema": {...}, "strict": True}` guarantees valid JSON matching the declared schema
- **Multi-step agents**: Define named steps under `steps` and declare a `first_step_name`; each step can have its own tools, instructions, and parser
- **Conditional routing**: Use `next_steps` with JSONPath conditions on the prior step's structured output
- **Scoped tools**: `allowed_tools: []` on a classifier step prevents tool calls during classification

---

### [Notebook 11: Agent Schedules](11-agent-schedules.ipynb)

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

### [Notebook 12: Calling REST APIs with `web_get`](12-web-get-tool.ipynb)

**What you'll learn:**
- Configure an agent with the inline `web_get` tool — a general-purpose HTTP client supporting `GET`/`POST`/`PUT`/`DELETE`/`HEAD`, custom headers, and request bodies
- Have the agent call a real REST API end-to-end (the demo uses public Open-Meteo so it runs out of the box; the same patterns apply to authenticated APIs and write/state-changing endpoints)
- Inspect `tool_input` / `tool_output` events to see exactly which request the agent made and what it got back
- Constrain the tool with `argument_override` to pin auth headers, method, timeout, and response-size limits in production
- Compare two integration patterns: a single generic `web_get` with endpoint guidance in the system prompt, vs. multiple specialized `web_get` registrations (one per operation) for sharper tool selection and per-operation guardrails

**What you'll build:**
A **Weather Assistant** agent that answers natural-language weather questions by chaining two calls to the [Open-Meteo](https://open-meteo.com/) public API (no signup required):
1. Geocode the city via `geocoding-api.open-meteo.com/v1/search`
2. Fetch current conditions via `api.open-meteo.com/v1/forecast`

The notebook iterates the agent through several configurations — a single generic `web_get`, a locked-down version with `argument_override`, specialized per-operation tools (`geocode_city`, `get_current_weather`), a POST tool that pushes a real notification via ntfy.sh, and a deliberately broken endpoint to demo failure handling — so you can see the trade-offs in each trace.

**Key concepts:**
- **`web_get` vs. `web_search`**: `web_get` issues an HTTP request to a specific endpoint the LLM (or your `argument_override`) chooses; `web_search` goes through a search engine. Use `web_get` for calling specific REST APIs — public or private, read or write.
- **`argument_override`**: Hardcode any subset of `WebGetToolParameters` (`url`, `method`, `headers`, `body`, `follow_redirects`, `timeout_seconds`, `max_content_bytes`, `ssl_verify`, `head_lines`/`tail_lines`). Pin an `Authorization` header for authenticated APIs, pin `method` to enforce read-only or write-only behavior, pin `url` when the agent should only talk to one endpoint.
- **Single tool vs. specialized tools**: A single `web_get` is fine for tutorials and one-off agents. For production, register `web_get` multiple times under different names — each with its own `description_template` and `argument_override` — to get sharper tool selection, per-operation auth/limits, and cleaner per-capability telemetry.
- **`web_get` argument shape**: The LLM-fillable arguments are HTTP-level (`url`/`method`/`headers`/`body`/...), not domain-typed (`city: str`). When you need typed function arguments, use `lambda` (in-process Python, no network) or `InlineMcpToolConfiguration` (external MCP server with proper typed functions).
- **Self-contained notebook**: requires only `VECTARA_API_KEY` (no corpora from earlier notebooks).

---

### [Notebook 13: Agent Skills — Progressive-Disclosure Instructions](13-agent-skills.ipynb)

**What you'll learn:**
- Configure an agent with a `skills` map — each skill is just `{description, content}` (caps: 500 / 50,000 chars)
- Watch the agent autonomously invoke a skill via the auto-exposed `invoke_skill` tool, and inspect the resulting `skill_load` event
- Trigger a skill from the client by sending an input message of type `"skill"` (no LLM round-trip needed for the decision)
- Define multiple skills and let the model pick the right one per question
- Use per-step `allowed_skills` to restrict which skills are available in a given step of a multi-step agent

**What you'll build:**
A **Support Copilot** agent whose system prompt stays small. A `customer_escalation` skill is registered with a short description (always visible to the model) and a long structured runbook — severity rubric, routing rules, draft-reply template, and an internal handoff note — that loads only when an inbound message actually looks like an outage or angry customer. A second `feature_request_intake` skill is added so you can see the model select between the two on different inbound messages (an SSO/Okta ask vs. a missing-dashboards incident).

**Key concepts:**
- **Progressive disclosure**: only the *short description* lives in the system prompt every turn; the heavy *content* enters context lazily — the token-economy win that makes skills different from just-stuff-the-prompt.
- **Two invocation paths**: `invoke_skill` is an auto-exposed tool the model can call; alternatively, the client can preload by sending `{"type": "skill", "skill_name": "..."}` in an event's `messages` array (e.g. a monitoring webhook that forces escalation mode). Both paths produce a `skill_load` event.
- **Skill vs. tool vs. sub-agent**: skills load *instructions*, tools provide *capabilities*, sub-agents bring their own *flow*. A common Vectara pairing: `corpora_search` over your help-center / runbook corpus answers "what's true," while skills answer "what should I do about it."
- **Self-contained notebook**: requires only `VECTARA_API_KEY` (no corpora from earlier notebooks).

---

### [Notebook 14: Agent Steps — Deterministic Plan Execution](14-agent-steps.ipynb)

**What you'll learn:**
- Build a sequential **plan-then-execute pipeline** where each phase has its own focused system prompt, tools, and structured-output schema
- Trace `step_transition` and `structured_output` events to make the deterministic flow visible
- Add a **conditional gate** that routes around expensive phases when prior output indicates they aren't needed
- Use **`reentry_step`** so follow-up turns enter a Q&A phase instead of re-running the whole pipeline
- Choose between steps, sub-agents, skills, and a single comprehensive prompt

**What you'll build:**
A **Contract Triage** agent that processes inbound documents through three sequential phases — `classify` (what kind of document is this?) → `extract` (pull key fields like parties, term, governing law) → `flag_issues` (Markdown risk-flag report). A second variant adds a conditional gate that exits early for inputs that aren't actually contracts. A third variant adds a `qa` step with `reentry_step` wired up so follow-up questions land in a dedicated Q&A phase that reuses already-extracted fields without re-running the pipeline.

**Key concepts:**
- **Steps vs. sub-agents**: steps share session history (each later phase can read what earlier phases produced); sub-agents start fresh in their own context. Steps are the right tool when phases need to *build on* each other.
- **Conditional transitions**: `next_steps` entries with UserFn `condition` expressions (`get('$.output.doc_type') == 'other'`) route on **typed structured-output fields**, not on the LLM's free-form text — the deterministic part of "deterministic plan execution".
- **`reentry_step`**: where the *next* user message in the same session lands. Use it to separate *one-shot pipeline runs* from *ongoing Q&A about what the pipeline produced*.
- **How this differs from notebook 10**: notebook 10 covers the **classifier-router fan-out** (one classifier branches to one of N terminal handlers). This notebook covers **sequential pipelines**, **conditional gating**, and **`reentry_step`** — read both for the full step-orchestration picture.
- **Self-contained notebook**: requires only `VECTARA_API_KEY` (no corpora from earlier notebooks).

---

## Tutorial Flow

```
1. Corpus Creation
   ↓
   Create two corpora with metadata attributes

2. Data Ingestion
   ↓
   Upload PDFs + Index crawled documentation

3. Deleting Documents
   ↓
   Remove documents by ID or metadata filter; reset a corpus

4. Query API
   ↓
   Search, filter, rerank, and generate answers

5. Agent API
   ↓
   Build autonomous agents with tools and context

6. Sub-Agents
   ↓
   Create multi-agent workflows with specialized sub-agents

7. Artifacts
   ↓
   Work with files in agent sessions

8. Lambda Tools for Data Analysis
   ↓
   Build NumPy/Pandas-powered data analysis tools

9. Reranker Instructions
   ↓
   Guide relevance scoring with domain-specific instructions

10. Structured Output & Multi-Step Agents
    ↓
    Constrain agent output to JSON schemas; route queries through multi-step flows

11. Agent Schedules
    ↓
    Automate agent runs on cron or interval schedules

12. Calling REST APIs with web_get
    ↓
    Give an agent the inline web_get tool to call any REST API (public or authenticated, read or write) at conversation time

13. Agent Skills
    ↓
    Attach progressive-disclosure instructions (description + content) so specialist guidance only enters context when the agent invokes it

14. Agent Steps — Deterministic Plan Execution
    ↓
    Drive an agent through a fixed sequence of phases (classify → extract → flag_issues) with conditional gates and reentry_step for follow-up Q&A
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

1. **Run notebooks in order** - Each notebook builds on the previous one, though notebooks 9, 10, and 11 only require the corpora from 1-2 and can be run independently of 4-8. Notebooks 3, 12, 13, and 14 are fully self-contained and only need a `VECTARA_API_KEY`.
2. **Corpus keys** - Save the corpus keys from Notebook 1, you'll need them in subsequent notebooks
3. **Agent reuse** - Notebooks 5 and 6 check if agents already exist before creating duplicates
4. **Rate limiting** - The notebooks include small delays between API calls to be respectful
5. **Cleanup** - Consider deleting test corpora/agents when done to keep your account organized
6. **Sub-agent dependencies** - Notebook 6 creates sub-agents first, then a parent orchestrator that references them

## Key API Endpoints Used

| Endpoint | Purpose | Notebook |
|----------|---------|----------|
| `POST /v2/corpora` | Create corpus | 1, 3 |
| `GET /v2/corpora` | List corpora | 1 |
| `POST /v2/corpora/{key}/upload_file` | Upload files | 2 |
| `POST /v2/corpora/{key}/documents` | Index documents | 2, 3 |
| `GET /v2/corpora/{key}/documents` | List documents | 2, 3 |
| `DELETE /v2/corpora/{key}/documents/{id}` | Delete one document | 3 |
| `DELETE /v2/corpora/{key}/documents` | Bulk delete documents (metadata filter / IDs) | 3 |
| `POST /v2/corpora/{key}/reset` | Delete all documents (reset corpus) | 3 |
| `DELETE /v2/corpora/{key}` | Delete corpus | 3 |
| `POST /v2/query` | Query corpora | 4, 9 |
| `POST /v2/agents` | Create agent | 5, 6, 7, 8, 10, 11, 12, 13, 14 |
| `POST /v2/agents/{key}/sessions` | Create session | 5, 6, 7, 8, 10, 12, 13, 14 |
| `POST /v2/agents/{key}/sessions/{key}/events` | Send messages / Upload artifacts | 5, 6, 7, 8, 10, 12, 13, 14 |
| `GET /v2/agents/{key}/sessions/{key}/events` | Get conversation history | 5, 11 |
| `GET /v2/agents/{key}/sessions/{key}/artifacts` | List session artifacts | 7 |
| `GET /v2/agents` | List agents | 6, 10, 11 |
| `DELETE /v2/agents/{key}` | Delete agent | 6, 7, 8, 10, 11, 12, 13, 14 |
| `POST /v2/tools` | Create Lambda tool | 6, 8 |
| `GET /v2/tools` | List Lambda tools | 6, 8 |
| `DELETE /v2/tools/{id}` | Delete Lambda tool | 6, 8 |
| `POST /v2/agents/{key}/schedules` | Create schedule | 11 |
| `GET /v2/agents/{key}/schedules` | List schedules | 11 |
| `PATCH /v2/agents/{key}/schedules/{key}` | Update schedule | 11 |
| `DELETE /v2/agents/{key}/schedules/{key}` | Delete schedule | 11 |
| `GET /v2/agents/{key}/schedules/{key}/executions` | Execution history | 11 |

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
