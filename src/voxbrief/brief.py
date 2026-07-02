"""Meeting intelligence: transcript -> structured brief, and Q&A over a transcript.

Both use JSON-schema-constrained output; the model never invents fields. For long
meetings, production would retrieve relevant transcript chunks (see README); this
reference passes the transcript in context, which is fine for demo-length meetings.
"""

from __future__ import annotations

from typing import Any

from voxbrief.llm import LLMBackend
from voxbrief.types import ActionItem, MeetingBrief, Transcript

BRIEF_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "decisions": {"type": "array", "items": {"type": "string"}},
        "action_items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "task": {"type": "string"},
                    "owner": {"type": "string"},
                    "due": {"type": "string"},
                },
                "required": ["task"],
            },
        },
        "topics": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["summary", "decisions", "action_items", "topics"],
}

_ANSWER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"answer": {"type": "string"}},
    "required": ["answer"],
}


def summarize(transcript: Transcript, backend: LLMBackend) -> MeetingBrief:
    """Extract a structured brief (summary, decisions, action items, topics)."""
    prompt = (
        "You are a meeting-intelligence assistant. From the transcript below, produce a "
        "concise summary, the decisions made, action items (with an owner when stated), "
        "and the main topics. Only use information present in the transcript.\n\n"
        f"TRANSCRIPT:\n{transcript.text}\n"
    )
    data = backend.complete(prompt, BRIEF_SCHEMA)
    return MeetingBrief(
        summary=data.get("summary", ""),
        decisions=list(data.get("decisions", [])),
        action_items=[
            ActionItem(task=a["task"], owner=a.get("owner"), due=a.get("due"))
            for a in data.get("action_items", [])
            if a.get("task")
        ],
        topics=list(data.get("topics", [])),
    )


def ask(transcript: Transcript, question: str, backend: LLMBackend) -> str:
    """Answer a question grounded in the transcript (the conversational layer)."""
    prompt = (
        "Answer the question using ONLY the meeting transcript below. If the answer is "
        "not in the transcript, say so.\n\n"
        f"TRANSCRIPT:\n{transcript.text}\n\nQUESTION: {question}\n"
    )
    data = backend.complete(prompt, _ANSWER_SCHEMA)
    return data.get("answer", "")
