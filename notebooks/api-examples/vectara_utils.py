"""Shared helpers for the api-examples notebooks.

Each notebook calls ``vectara_utils.configure(BASE_URL, headers)`` once after
its setup cell, then uses :func:`delete_and_create_agent` /
:func:`delete_and_create_tool` to idempotently (re)create agents and lambda
tools on every run without tripping over three Vectara-API realities:

- ``/v2/agents`` and ``/v2/tools`` list endpoints are paginated
- DELETE is asynchronous (a POST right after a DELETE can 409 "being deleted")
- Two overlapping deletes can race ("already exists" even though we just deleted)

On terminal failure the helpers raise so the real cause surfaces at the call
site instead of propagating ``None`` into later cells.
"""
import time

import requests


_BASE_URL = None
_HEADERS = None


def configure(base_url, headers):
    """Bind the Vectara API base URL and auth headers used by the helpers."""
    global _BASE_URL, _HEADERS
    _BASE_URL = base_url
    _HEADERS = headers


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


def delete_and_create_agent(agent_config, agent_name, max_attempts=4):
    """Delete any existing agent with this name, then create a fresh one."""
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
        r.raise_for_status()
    raise RuntimeError(f"Failed to create agent '{agent_name}' after {max_attempts} attempts")


def delete_and_create_tool(tool_config, tool_name, max_attempts=4):
    """Delete any existing tool with this name, then create a fresh one.

    Callers must delete any agent that references this tool BEFORE invoking,
    otherwise the server rejects DELETE with "tool is being used in different
    configurations" and the retry loop cannot recover on its own.
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
        r.raise_for_status()
    raise RuntimeError(f"Failed to create tool '{tool_name}' after {max_attempts} attempts")
