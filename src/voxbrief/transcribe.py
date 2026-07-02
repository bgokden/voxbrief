"""Speech-to-text. Pluggable ``Transcriber`` protocol + a local Whisper backend.

Swap in an enterprise/streaming STT (with speaker diarization) by implementing the
same protocol — see the README "From demo to production".
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from voxbrief.types import Segment, Transcript


@runtime_checkable
class Transcriber(Protocol):
    def transcribe(self, audio_path: str) -> Transcript: ...


class FasterWhisperTranscriber:
    """Local Whisper via faster-whisper (CTranslate2). Install ``voxbrief[whisper]``.

    Runs on CPU; pick a small model (``tiny``/``base``) for demos, larger for quality.
    """

    def __init__(self, model_size: str = "base", device: str = "cpu", compute_type: str = "int8") -> None:
        from faster_whisper import WhisperModel  # lazy optional import

        self._model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe(self, audio_path: str) -> Transcript:
        segments, _info = self._model.transcribe(audio_path)
        return Transcript(
            segments=[Segment(start=s.start, end=s.end, text=s.text) for s in segments]
        )
