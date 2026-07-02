"""Real end-to-end test (opt-in): audio -> Whisper -> LLM brief -> Q&A.

Skipped by default and in CI. Run locally:
    VOXBRIEF_INTEGRATION=1 pytest tests/test_integration.py -q
Requires: pip install -e ".[whisper]", Ollama running with a model
(default llama3.2:3b; override with VOXBRIEF_OLLAMA_MODEL), and the demo audio
(python examples/make_demo_audio.py).
"""

import os

import pytest

from voxbrief.brief import ask, summarize


@pytest.mark.integration
def test_end_to_end_meeting():
    if os.environ.get("VOXBRIEF_INTEGRATION") != "1":
        pytest.skip("set VOXBRIEF_INTEGRATION=1 (with Whisper + Ollama) to run")
    audio = os.path.join(os.path.dirname(__file__), "..", "examples", "demo_meeting.aiff")
    if not os.path.exists(audio):
        pytest.skip("run examples/make_demo_audio.py first")

    from voxbrief.llm import OllamaBackend
    from voxbrief.transcribe import FasterWhisperTranscriber

    tr = FasterWhisperTranscriber(os.environ.get("VOXBRIEF_WHISPER_MODEL", "tiny")).transcribe(audio)
    assert "onboarding" in tr.text.lower() or "tuesday" in tr.text.lower()

    backend = OllamaBackend(os.environ.get("VOXBRIEF_OLLAMA_MODEL", "llama3.2:3b"), temperature=0.1)
    brief = summarize(tr, backend)
    assert brief.summary and brief.action_items  # produced a real brief

    answer = ask(tr, "When do we launch?", backend)
    assert answer
