"""Smoke test the MCP wiring (no audio, no model)."""

import asyncio

from voxbrief.server import mcp


def test_server_name():
    assert mcp.name == "voxbrief"


def test_tools_registered():
    tools = asyncio.run(mcp.list_tools())
    names = {t.name for t in tools}
    assert {"transcribe", "summarize_meeting", "ask_meeting"} <= names
