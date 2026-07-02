"""Offline tests: the transcript -> brief / Q&A logic via FakeBackend.

No audio, no Whisper, no model download. Real STT + LLM are exercised by the
gated integration test.
"""

from voxbrief import FakeBackend, Segment, Transcript, ask, summarize

TRANSCRIPT = Transcript(
    segments=[
        Segment(0.0, 4.0, "Alice: Let's ship the new onboarding flow next Tuesday."),
        Segment(4.0, 8.0, "Bob: Agreed. I'll handle the API changes by Monday."),
        Segment(8.0, 12.0, "Alice: Great, decision made. Carol, can you update the docs?"),
        Segment(12.0, 15.0, "Carol: Yes, I'll update the docs by Wednesday."),
    ]
)


def test_transcript_text_joins_segments():
    assert "onboarding flow" in TRANSCRIPT.text
    assert "update the docs" in TRANSCRIPT.text


def test_summarize_maps_structured_output():
    fake = FakeBackend(
        [
            {
                "summary": "Team agreed to ship onboarding next Tuesday.",
                "decisions": ["Ship the new onboarding flow next Tuesday"],
                "action_items": [
                    {"task": "Handle the API changes", "owner": "Bob", "due": "Monday"},
                    {"task": "Update the docs", "owner": "Carol", "due": "Wednesday"},
                ],
                "topics": ["onboarding", "release"],
            }
        ]
    )
    brief = summarize(TRANSCRIPT, fake)
    assert brief.summary.startswith("Team agreed")
    assert brief.decisions == ["Ship the new onboarding flow next Tuesday"]
    assert len(brief.action_items) == 2
    assert brief.action_items[0].owner == "Bob"
    assert brief.action_items[1].task == "Update the docs"
    assert "onboarding" in brief.topics
    # serializable
    d = brief.to_dict()
    assert d["action_items"][0]["due"] == "Monday"


def test_summarize_skips_action_items_without_task():
    fake = FakeBackend(
        [{"summary": "s", "decisions": [], "action_items": [{"owner": "X"}], "topics": []}]
    )
    brief = summarize(TRANSCRIPT, fake)
    assert brief.action_items == []


def test_ask_returns_grounded_answer():
    fake = FakeBackend([{"answer": "Bob will handle the API changes by Monday."}])
    answer = ask(TRANSCRIPT, "Who is doing the API changes?", fake)
    assert "Bob" in answer
