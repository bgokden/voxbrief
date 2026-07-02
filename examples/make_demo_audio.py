"""Synthesize a short fake meeting to audio so the demo is reproducible and
privacy-safe (no real recordings).

    python examples/make_demo_audio.py            # -> examples/demo_meeting.aiff
    voxbrief summarize examples/demo_meeting.aiff

macOS uses `say`; on Linux install espeak-ng and run:
    espeak-ng -w examples/demo_meeting.wav -f examples/demo_meeting.txt
"""

import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(__file__)
SCRIPT = os.path.join(HERE, "demo_meeting.txt")


def main() -> int:
    text = open(SCRIPT, encoding="utf-8").read()
    if shutil.which("say"):  # macOS
        out = os.path.join(HERE, "demo_meeting.aiff")
        subprocess.run(["say", "-o", out, text], check=True)
        print(f"wrote {out}")
        return 0
    if shutil.which("espeak-ng"):  # Linux
        out = os.path.join(HERE, "demo_meeting.wav")
        subprocess.run(["espeak-ng", "-w", out, "-f", SCRIPT], check=True)
        print(f"wrote {out}")
        return 0
    print("No TTS found. Install macOS `say` or `espeak-ng`.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
