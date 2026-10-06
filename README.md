# example-notebooks
This repository contains example code for Vectara.
* Notebooks used in our blog posts
* Examples for how to use Vectara with LlamaIndex, LangChain and DSPy.

## API Examples Tutorial Series

A step-by-step tutorial series in `notebooks/api-examples/` covering the Vectara API v2:

1. [Corpus Creation](notebooks/api-examples/1-corpus-creation.ipynb) — Create and configure corpora
2. [Data Ingestion](notebooks/api-examples/2-data-ingestion.ipynb) — Upload and index documents
3. [Deleting Documents](notebooks/api-examples/3-document-deletion.ipynb) — Delete by ID, bulk delete by metadata filter, reset a corpus
4. [Query API](notebooks/api-examples/4-query-api.ipynb) — Search, retrieval, and generation
5. [Agent API](notebooks/api-examples/5-agent-api.ipynb) — Build RAG agents
6. [Sub-Agents](notebooks/api-examples/6-sub-agents.ipynb) — Multi-agent orchestration
7. [Artifacts](notebooks/api-examples/7-artifacts.ipynb) — Working with artifacts
8. [Lambda Tools for Data Analysis](notebooks/api-examples/8-lambda-tools-data-analysis.ipynb) — NumPy/Pandas lambda tools for agent data analysis
9. [Reranker Instructions](notebooks/api-examples/9-reranker-instructions.ipynb) — Using reranker instructions with qwen3-reranker for role-based intent steering and jargon resolution
10. [Structured Output & Multi-Step Agents](notebooks/api-examples/10-structured-output-multi-step.ipynb) — JSON-schema output and step routing
11. [Agent Schedules](notebooks/api-examples/11-agent-schedules.ipynb) — Run agents on cron or interval schedules
12. [Calling REST APIs with `web_get`](notebooks/api-examples/12-web-get-tool.ipynb) — Let agents call external REST APIs
13. [Agent Skills](notebooks/api-examples/13-agent-skills.ipynb) — Load specialist instructions on demand
14. [Agent Steps](notebooks/api-examples/14-agent-steps.ipynb) — Deterministic multi-phase pipelines
15. [`$ref` Secrets and Access Control](notebooks/api-examples/15-ref-secrets-and-access-control.ipynb) — Per-session retrieval scoping and credential injection
16. [Agent Aliases](notebooks/api-examples/16-agent-aliases.ipynb) — Canary rollouts and tenant routing behind a stable alias
17. [Cross-Tenant Query with `web_get`](notebooks/api-examples/17-cross-tenant-query-web-get.ipynb) — Query a corpus in another Vectara account with a scoped key stored as an agent secret
