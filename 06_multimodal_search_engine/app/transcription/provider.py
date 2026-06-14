from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TranscriptSegment:
    start: float
    end: float
    text: str


class TranscriptionProvider:
    async def transcribe(self, path: Path) -> list[TranscriptSegment]:
        sidecar = path.with_suffix(path.suffix + ".txt")
        if sidecar.exists():
            return parse_transcript(sidecar.read_text(encoding="utf-8"))

        words = path.stem.replace("_", " ").replace("-", " ")
        text = f"Media file named {words}".strip()
        return [TranscriptSegment(start=0.0, end=0.0, text=text)] if text else []


def parse_transcript(raw_text: str) -> list[TranscriptSegment]:
    segments: list[TranscriptSegment] = []
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if "|" not in line:
            segments.append(TranscriptSegment(start=0.0, end=0.0, text=line))
            continue
        timing, text = line.split("|", 1)
        start, end = timing.split("-", 1)
        segments.append(
            TranscriptSegment(
                start=float(start.strip()),
                end=float(end.strip()),
                text=text.strip(),
            ),
        )
    return segments
