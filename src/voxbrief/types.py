"""Core data types for meeting intelligence."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Segment:
    """A transcribed span of audio."""

    start: float  # seconds
    end: float
    text: str
    speaker: str | None = None  # populated by diarization in production


@dataclass
class Transcript:
    segments: list[Segment]

    @property
    def text(self) -> str:
        return " ".join(s.text.strip() for s in self.segments if s.text.strip())

    def to_dict(self) -> dict:
        return {
            "segments": [
                {"start": s.start, "end": s.end, "text": s.text, "speaker": s.speaker}
                for s in self.segments
            ],
            "text": self.text,
        }


@dataclass
class ActionItem:
    task: str
    owner: str | None = None
    due: str | None = None


@dataclass
class MeetingBrief:
    """Structured intelligence extracted from a meeting transcript."""

    summary: str
    decisions: list[str] = field(default_factory=list)
    action_items: list[ActionItem] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "summary": self.summary,
            "decisions": self.decisions,
            "action_items": [
                {"task": a.task, "owner": a.owner, "due": a.due} for a in self.action_items
            ],
            "topics": self.topics,
        }
