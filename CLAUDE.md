# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a collection of Jupyter notebooks demonstrating how to use the Vectara RAG (Retrieval Augmented Generation) platform with various integrations including LangChain, LlamaIndex, and DSPy. The notebooks are designed to run in Google Colab.

## Key Technologies

- **Vectara**: RAG-as-a-service platform providing text extraction, ML-based chunking, Boomerang embeddings, hybrid search, and LLM summarization (Mockingbird)
- **LangChain**: Use `langchain-vectara` package for integration
- **LlamaIndex**: Use `llama-index-indices-managed-vectara` package (v0.4.0+ uses API v2)
- **vectara-agentic**: Vectara's agentic RAG package built on LlamaIndex

## Environment Variables

Notebooks typically require these environment variables:
- `VECTARA_API_KEY`: Vectara API key
- `VECTARA_CORPUS_KEY`: Vectara corpus identifier
- `OPENAI_API_KEY`: Required for some notebooks that use OpenAI models

## Running Notebooks

Notebooks are designed to run in Google Colab. Each notebook includes a Colab badge link at the top. They can also be run locally with Jupyter:

```bash
pip install jupyter
jupyter notebook notebooks/
```

## Data Files

Sample data for notebooks is in `data/`:
- PDF files (transformer papers, policy docs, etc.)
- Text files (state_of_the_union.txt, paul_graham_essay.txt)

## Notebook Patterns

1. **File upload to Vectara**: Use `add_files()` or `insert_file()` - Vectara handles chunking and embedding
2. **Querying**: Use `as_query_engine()` for retrieval, `as_chat_engine()` for conversational interfaces
3. **Streaming**: Set `streaming=True` in query engine for streamed responses
4. **Reranking options**: MMR (diversity), Slingshot (multilingual), UDF (custom functions), chain reranker
