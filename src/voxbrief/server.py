"""MCP server: give any MCP client (Claude Desktop, Cursor, ...) meeting tools.

Tools: transcribe, summarize_meeting, ask_meeting. Heavy backends load lazily on
first use, so the server starts instantly.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

from mcp.server.fastmcp import FastMCP

from voxbrief.brief import ask, summarize
from voxbrief.transcribe import FasterWhisperTranscriber

mcp = FastMCP("voxbrief")


@lru_cache(maxsize=1)
def _transcriber() -> FasterWhisperTranscriber:
    return FasterWhisperTranscriber(model_size=os.environ.get("VOXBRIEF_WHISPER_MODEL", "base"))


@lru_cache(maxsize=1)
def _backend():
    from voxbrief.llm import OllamaBackend

    return OllamaBackend(model=os.environ.get("VOXBRIEF_OLLAMA_MODEL", "llama3.1"))


@mcp.tool()
def transcribe(audio_path: str) -> dict[str, Any]:
    """Transcribe an audio file (wav/mp3/m4a/...) to text with timestamps."""
    return _transcriber().transcribe(audio_path).to_dict()


@mcp.tool()
def summarize_meeting(audio_path: str) -> dict[str, Any]:
    """Transcribe a meeting recording and return a structured brief:
    summary, decisions, action items (with owners), and topics."""
    transcript = _transcriber().transcribe(audio_path)
    return summarize(transcript, _backend()).to_dict()


@mcp.tool()
def ask_meeting(audio_path: str, question: str) -> str:
    """Answer a question grounded in a meeting recording's transcript."""
    transcript = _transcriber().transcribe(audio_path)
    return ask(transcript, question, _backend())


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
