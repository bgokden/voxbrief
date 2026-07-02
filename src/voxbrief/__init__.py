"""voxbrief — local meeting-intelligence agent (transcribe -> brief -> Q&A)."""

from voxbrief.brief import BRIEF_SCHEMA, ask, summarize
from voxbrief.llm import FakeBackend, LlamaCppBackend, LLMBackend, OllamaBackend
from voxbrief.types import ActionItem, MeetingBrief, Segment, Transcript

__version__ = "0.1.0"

__all__ = [
    "Transcript",
    "Segment",
    "MeetingBrief",
    "ActionItem",
    "summarize",
    "ask",
    "BRIEF_SCHEMA",
    "LLMBackend",
    "OllamaBackend",
    "LlamaCppBackend",
    "FakeBackend",
]
