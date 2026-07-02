# voxbrief

[![CI](https://github.com/bgokden/voxbrief/actions/workflows/ci.yml/badge.svg)](https://github.com/bgokden/voxbrief/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)

A **local meeting-intelligence agent**: turn a meeting recording into a structured
brief — **summary, decisions, action items (with owners), topics** — and then **ask
questions grounded in the transcript**. Runs fully local (Whisper + a local LLM with
structured output), and ships as a **library, a CLI, and an MCP server** so Claude
Desktop / Cursor can use it as a tool.

> This is a clean, self-contained **reference implementation**. A production system
> (see [From demo to production](#from-demo-to-production-enterprise)) adds diarization,
> PII redaction, streaming, enterprise LLMs, evaluation, and at-scale deployment.

## Pipeline

```
audio ──▶ Whisper (local STT) ──▶ transcript ──▶ LLM (structured output) ──▶ brief
                                              └─▶ Q&A grounded in transcript
```

## Demo (real output)

```bash
python examples/make_demo_audio.py          # synthesize a short fake meeting (privacy-safe)
voxbrief summarize examples/demo_meeting.aiff
```

```json
{
  "summary": "The meeting discussed the launch date for the new onboarding flow. The decision was made to launch it next Tuesday, provided API changes are completed by Monday.",
  "decisions": ["Launch the onboarding flow next Tuesday"],
  "action_items": [
    {"task": "Finish API changes", "owner": "Bob", "due": "Monday"},
    {"task": "Update documentation and help center", "owner": "Carol", "due": "Wednesday"},
    {"task": "Prepare announcement for marketing", "owner": "Bob", "due": "This afternoon"}
  ],
  "topics": ["Launch date for new onboarding flow"]
}
```

```bash
voxbrief ask examples/demo_meeting.aiff "Who is doing the API changes and by when?"
# -> Bob, by Monday
```

*(Real run: Whisper `tiny` for STT, `llama3.2:3b` via Ollama for the brief.)*

## Install

```bash
pip install "voxbrief[whisper]"     # + faster-whisper for local STT
```

You also need a local LLM. Easiest is [Ollama](https://ollama.com):

```bash
ollama pull llama3.2:3b
```

## CLI

```bash
voxbrief transcribe meeting.m4a
voxbrief summarize  meeting.m4a
voxbrief ask        meeting.m4a "What did we decide about pricing?"
```

## MCP server (Claude Desktop / Cursor)

```json
{
  "mcpServers": {
    "voxbrief": { "command": "voxbrief-mcp" }
  }
}
```

Tools: `transcribe`, `summarize_meeting`, `ask_meeting`.

## Library

```python
from voxbrief import summarize, ask
from voxbrief.transcribe import FasterWhisperTranscriber
from voxbrief.llm import OllamaBackend

transcript = FasterWhisperTranscriber("base").transcribe("meeting.m4a")
backend = OllamaBackend("llama3.2:3b")

brief = summarize(transcript, backend)        # -> MeetingBrief
answer = ask(transcript, "When do we launch?", backend)
```

## Architecture

Two small protocols keep it swappable:

- **`Transcriber`** — `transcribe(audio) -> Transcript`. Reference: `FasterWhisperTranscriber`.
- **`LLMBackend`** — `complete(prompt, schema) -> dict` (JSON-schema-constrained).
  Backends: `OllamaBackend` (local, default), `LlamaCppBackend` (GGUF), `FakeBackend`
  (offline tests). Any vLLM / enterprise endpoint plugs in via the same protocol.

The brief and Q&A use **structured output** — the model fills a JSON schema, so fields
are never invented and spans/answers stay grounded.

## From demo to production (enterprise)

This repo is deliberately the clean core. A production meeting-intelligence system
swaps components behind the same interfaces and adds:

- **Speaker diarization** — who said what (WhisperX / pyannote), so action items get
  the *right* owner automatically.
- **Streaming / real-time** transcription and live summaries, not just batch files.
- **PII redaction + guardrails** before any LLM call (OWASP LLM Top 10); enterprise
  LLMs under a BAA (Azure OpenAI, Bedrock) instead of local models.
- **Long meetings** — chunking + retrieval (RAG) and long-term (vector-backed) memory
  instead of stuffing the full transcript into context.
- **Evaluation & observability** — quality metrics, LLM-as-judge, tracing
  (Arize Phoenix / LangSmith), and eval-gated CI/CD.
- **Integrations** — calendar, CRM, and Slack/Jira to auto-file action items where
  work actually happens.
- **Scale & governance** — RBAC, multi-tenant, audit logs, and CI/CD to containers on
  AWS serving thousands of users.

## Development

```bash
pip install -e ".[dev]"
pytest                      # offline core tests (FakeBackend, no audio/model)
```

Real STT + LLM are exercised by a gated integration test (opt-in via
`VOXBRIEF_INTEGRATION=1`, with Ollama running) and verified locally end-to-end.

## License

MIT © [Berk Gökden](https://berkgokden.com)
