"""CLI: voxbrief transcribe|summarize|ask <audio> ..."""

from __future__ import annotations

import argparse
import json
import os
import sys

from voxbrief import __version__


def _transcriber():
    from voxbrief.transcribe import FasterWhisperTranscriber

    return FasterWhisperTranscriber(model_size=os.environ.get("VOXBRIEF_WHISPER_MODEL", "base"))


def _backend():
    from voxbrief.llm import OllamaBackend

    return OllamaBackend(model=os.environ.get("VOXBRIEF_OLLAMA_MODEL", "llama3.1"))


def _cmd_transcribe(args) -> int:
    t = _transcriber().transcribe(args.audio)
    print(t.text)
    return 0


def _cmd_summarize(args) -> int:
    from voxbrief.brief import summarize

    t = _transcriber().transcribe(args.audio)
    print(json.dumps(summarize(t, _backend()).to_dict(), indent=2, ensure_ascii=False))
    return 0


def _cmd_ask(args) -> int:
    from voxbrief.brief import ask

    t = _transcriber().transcribe(args.audio)
    print(ask(t, args.question, _backend()))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="voxbrief", description="Local meeting-intelligence agent")
    p.add_argument("--version", action="version", version=f"voxbrief {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    t = sub.add_parser("transcribe", help="Transcribe audio to text")
    t.add_argument("audio")
    t.set_defaults(func=_cmd_transcribe)

    s = sub.add_parser("summarize", help="Transcribe + structured meeting brief")
    s.add_argument("audio")
    s.set_defaults(func=_cmd_summarize)

    a = sub.add_parser("ask", help="Ask a question grounded in the meeting")
    a.add_argument("audio")
    a.add_argument("question")
    a.set_defaults(func=_cmd_ask)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
