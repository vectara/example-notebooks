"""Shared helpers for the api-examples notebooks.

Each notebook calls ``vectara_utils.configure(BASE_URL, headers)`` once after
its setup cell, then uses these helpers to do the API plumbing without
re-implementing it inline:

- :func:`delete_and_create_agent` / :func:`delete_and_create_tool` —
  idempotently (re)create agents and lambda tools on every run.
- :func:`create_session` — POST a session and return its key.
- :func:`send_event` — POST messages (text or skill) to a session and return
  the parsed events list.
- :func:`wait_for_agent_gone` — poll until an agent's async DELETE clears.
- :func:`make_headers` — build the standard auth headers from
  ``VECTARA_API_KEY`` (saves the boilerplate dict in every notebook).

The helpers paper over three Vectara-API realities:

- ``/v2/agents`` and ``/v2/tools`` list endpoints are paginated
- DELETE is asynchronous (a POST right after a DELETE can 409 "being deleted")
- Two overlapping deletes can race ("already exists" even though we just deleted)

On terminal failure the helpers raise so the real cause surfaces at the call
site instead of propagating ``None`` into later cells.
"""
import os
import time
from datetime import datetime

import requests


_BASE_URL = None
_HEADERS = None


def configure(base_url, headers):
    """Bind the Vectara API base URL and auth headers used by the helpers."""
    global _BASE_URL, _HEADERS
    _BASE_URL = base_url
    _HEADERS = headers


def make_headers(api_key=None):
    """Return the standard Vectara API headers dict.

    If ``api_key`` is None, reads from the ``VECTARA_API_KEY`` environment
    variable. Saves the small boilerplate block every notebook used to inline.
    """
    if api_key is None:
        api_key = os.environ["VECTARA_API_KEY"]
    return {"x-api-key": api_key, "Content-Type": "application/json"}


def create_session(agent_key, name=None, metadata=None):
    """Create a session for ``agent_key`` and return its key.

    ``name`` defaults to a timestamped string if None. ``metadata`` is an
    optional dict attached to the session. Raises on non-201.
    """
    if name is None:
        name = f"Session {datetime.now().strftime('%Y%m%d-%H%M%S')}"
    payload = {"name": name}
    if metadata is not None:
        payload["metadata"] = metadata
    r = requests.post(
        f"{_BASE_URL}/agents/{agent_key}/sessions",
        headers=_HEADERS,
        json=payload,
    )
    r.raise_for_status()
    return r.json()["key"]


def send_event(agent_key, session_key, messages, stream_response=False):
    """POST an event to a session and return the parsed ``events`` list.

    ``messages`` is the list passed straight to the API, e.g.
        [{"type": "text",  "content": "hello"}]
    or  [{"type": "skill", "skill_name": "code_review"}]

    Raises on non-201. The caller is responsible for whatever per-notebook
    pretty-printing of the returned events makes sense for its trace.
    """
    payload = {"messages": messages, "stream_response": stream_response}
    r = requests.post(
        f"{_BASE_URL}/agents/{agent_key}/sessions/{session_key}/events",
        headers=_HEADERS,
        json=payload,
    )
    r.raise_for_status()
    return r.json().get("events", [])


def wait_for_agent_gone(name, timeout=30, poll_interval=2):
    """Poll until no agents matching ``name`` are visible (async DELETE).

    Returns True if the agent is gone before ``timeout`` seconds elapse,
    False otherwise. Use this between an agent DELETE and any operation
    that the lingering agent would block (e.g. deleting a tool the agent
    still references).
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not any(True for _ in find_agents_by_name(name)):
            return True
        time.sleep(poll_interval)
    return False


def clear_corpus_documents(corpus_key, request_timeout=30):
    """Delete every document in a corpus, paging through the list endpoint.

    Adds the resilience the inline cleanup loops in `2-data-ingestion.ipynb`
    used to lack: explicit per-call HTTP timeout, plus one retry with
    exponential backoff on transient network/gateway errors
    (RequestException, 502/503/504). A single network blip on any one
    DELETE no longer kills the whole loop.

    Returns the number of documents successfully deleted.
    """
    deleted = 0
    page_key = None
    while True:
        params = {"limit": 100}
        if page_key:
            params["page_key"] = page_key

        # Resilient list call.
        resp = _request_with_retry(
            "GET",
            f"{_BASE_URL}/corpora/{corpus_key}/documents",
            headers=_HEADERS,
            params=params,
            timeout=request_timeout,
        )
        if resp is None or resp.status_code != 200:
            status = resp.status_code if resp is not None else "no response"
            print(f"Error listing documents from '{corpus_key}': {status}")
            return deleted

        data = resp.json()
        documents = data.get("documents", [])
        if not documents:
            break

        for doc in documents:
            doc_id = doc["id"]
            del_resp = _request_with_retry(
                "DELETE",
                f"{_BASE_URL}/corpora/{corpus_key}/documents/{doc_id}",
                headers=_HEADERS,
                timeout=request_timeout,
            )
            if del_resp is not None and del_resp.status_code in (200, 204):
                deleted += 1
            else:
                status = del_resp.status_code if del_resp is not None else "no response"
                print(f"  Failed to delete {doc_id}: {status}")

        page_key = data.get("metadata", {}).get("page_key")
        if not page_key:
            break
    return deleted


def _request_with_retry(method, url, *, max_retries=2, **kwargs):
    """Issue an HTTP request with one retry on transient errors.

    Returns the final ``Response`` if the call ever produced one (even a
    non-2xx), or ``None`` if every attempt raised. Callers inspect
    ``status_code`` themselves; this helper only owns the retry policy.

    Retries on:
    - ``requests.exceptions.RequestException`` (timeout, connection error)
    - HTTP 502/503/504 (transient gateway/service errors)
    """
    last_response = None
    for attempt in range(max_retries + 1):
        try:
            r = requests.request(method, url, **kwargs)
        except requests.exceptions.RequestException as exc:
            last_response = None
            if attempt < max_retries:
                time.sleep(2 ** attempt)
                continue
            print(f"  Network error after {attempt + 1} attempt(s) on {method} {url}: {exc}")
            return None
        last_response = r
        if r.status_code in _TRANSIENT_STATUSES and attempt < max_retries:
            time.sleep(2 ** attempt)
            continue
        return r
    return last_response


def _iter_paginated(path, key):
    """Yield every item from a paginated ``/v2/<path>`` list endpoint."""
    page_key = None
    while True:
        params = {"limit": 100}
        if page_key:
            params["page_key"] = page_key
        r = requests.get(f"{_BASE_URL}/{path}", headers=_HEADERS, params=params)
        r.raise_for_status()
        data = r.json()
        for item in data.get(key, []):
            yield item
        page_key = data.get("metadata", {}).get("page_key")
        if not page_key:
            return


def find_agents_by_name(name):
    """Yield every agent whose ``name`` matches, paginating through all pages."""
    return (a for a in _iter_paginated("agents", "agents") if a.get("name") == name)


def find_tools_by_name(name):
    """Yield every tool whose ``name`` matches, paginating through all pages."""
    return (t for t in _iter_paginated("tools", "tools") if t.get("name") == name)


# Transient gateway / service-unavailable statuses that warrant an automatic
# retry with exponential backoff. We do NOT include 500 because it sometimes
# indicates a real schema validation failure that retrying would just repeat.
_TRANSIENT_STATUSES = (502, 503, 504)


def delete_and_create_agent(agent_config, agent_name, max_attempts=4):
    """Delete any existing agent with this name, then create a fresh one.

    Retries on:
    - 409 (existing-conflict) — re-delete and retry, handling the async-DELETE race.
    - 502 / 503 / 504 (transient gateway/service errors) — wait and retry.

    Other non-201 statuses surface as ``HTTPError`` immediately.
    """
    for existing in find_agents_by_name(agent_name):
        dr = requests.delete(f"{_BASE_URL}/agents/{existing['key']}", headers=_HEADERS)
        if dr.status_code == 204:
            print(f"Deleted existing agent '{agent_name}' ({existing['key']})")
        else:
            print(f"Warning: failed to delete {existing['key']}: {dr.text}")

    for attempt in range(max_attempts):
        r = requests.post(f"{_BASE_URL}/agents", headers=_HEADERS, json=agent_config)
        if r.status_code == 201:
            data = r.json()
            print(f"Created agent '{agent_name}' (key: {data['key']})")
            return data["key"]
        if r.status_code == 409 and attempt < max_attempts - 1:
            wait = 2 ** attempt
            print(f"409 on create ({r.text[:120]}); retrying in {wait}s...")
            for existing in find_agents_by_name(agent_name):
                requests.delete(f"{_BASE_URL}/agents/{existing['key']}", headers=_HEADERS)
            time.sleep(wait)
            continue
        if r.status_code in _TRANSIENT_STATUSES and attempt < max_attempts - 1:
            wait = 2 ** attempt
            print(f"{r.status_code} on create (transient); retrying in {wait}s...")
            time.sleep(wait)
            continue
        r.raise_for_status()
    raise RuntimeError(f"Failed to create agent '{agent_name}' after {max_attempts} attempts")


def delete_and_create_tool(tool_config, tool_name, max_attempts=4):
    """Delete any existing tool with this name, then create a fresh one.

    Callers must delete any agent that references this tool BEFORE invoking,
    otherwise the server rejects DELETE with "tool is being used in different
    configurations" and the retry loop cannot recover on its own.

    Retries on 409 (existing-conflict, by re-deleting) and on 502/503/504
    (transient gateway errors, by waiting). Other non-201s raise immediately.
    """
    for existing in find_tools_by_name(tool_name):
        dr = requests.delete(f"{_BASE_URL}/tools/{existing['id']}", headers=_HEADERS)
        if dr.status_code == 204:
            print(f"Deleted existing tool '{tool_name}' ({existing['id']})")
        else:
            print(f"Warning: failed to delete {existing['id']}: {dr.text}")

    for attempt in range(max_attempts):
        r = requests.post(f"{_BASE_URL}/tools", headers=_HEADERS, json=tool_config)
        if r.status_code == 201:
            data = r.json()
            print(f"Created tool '{tool_name}' (id: {data['id']})")
            return data["id"]
        if r.status_code == 409 and attempt < max_attempts - 1:
            wait = 2 ** attempt
            print(f"409 on create ({r.text[:120]}); retrying in {wait}s...")
            for existing in find_tools_by_name(tool_name):
                requests.delete(f"{_BASE_URL}/tools/{existing['id']}", headers=_HEADERS)
            time.sleep(wait)
            continue
        if r.status_code in _TRANSIENT_STATUSES and attempt < max_attempts - 1:
            wait = 2 ** attempt
            print(f"{r.status_code} on create (transient); retrying in {wait}s...")
            time.sleep(wait)
            continue
        r.raise_for_status()
    raise RuntimeError(f"Failed to create tool '{tool_name}' after {max_attempts} attempts")
