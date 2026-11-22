"""Generate reusable US-English neural MP3 files for the public briefing player."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
AUDIO = ROOT / "audio"
VOICE = "en-US-JennyNeural"
RATE = "-8%"


def segments(briefing: dict) -> list[str]:
    result: list[str] = []
    for item in briefing["items"]:
        result.append(item["title"])
        result.extend(item["summary"])
        result.append(item["why"])
        for point in item["language"]:
            result.extend([point["term"], point["example"]])
    for point in briefing.get("further", []):
        result.extend([point["term"], point["example"]])
    return result


async def write_audio(text: str, output: Path) -> None:
    if output.exists() and output.stat().st_size > 512:
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    await edge_tts.Communicate(text, voice=VOICE, rate=RATE).save(str(output))


async def main() -> None:
    jobs: list[tuple[str, Path]] = []
    for source in sorted(DATA.glob("*.json")):
        if source.name == "index.json":
            continue
        briefing = json.loads(source.read_text(encoding="utf-8"))
        folder = AUDIO / briefing["date"]
        for index, text in enumerate(segments(briefing)):
            jobs.append((text, folder / f"{index:03d}.mp3"))
    for text, output in jobs:
        await write_audio(text, output)


if __name__ == "__main__":
    asyncio.run(main())
