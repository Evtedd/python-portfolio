from pathlib import Path

from app.ingestion.pdf import extract_pdf_pages
from app.ingestion.types import ExtractedText
from app.models import AssetKind
from app.transcription.provider import TranscriptionProvider


class Extractor:
    def __init__(self, transcription: TranscriptionProvider) -> None:
        self.transcription = transcription

    async def extract(self, kind: AssetKind, path: Path) -> list[ExtractedText]:
        if kind == AssetKind.pdf:
            return extract_pdf_pages(path.read_bytes())
        if kind in {AssetKind.audio, AssetKind.video}:
            segments = await self.transcription.transcribe(path)
            return [
                ExtractedText(
                    text=segment.text,
                    start_seconds=segment.start,
                    end_seconds=segment.end,
                )
                for segment in segments
            ]
        if kind == AssetKind.image:
            caption = path.stem.replace("_", " ").replace("-", " ")
            return [ExtractedText(text=f"Image: {caption}", preview_path=str(path))]
        raise ValueError(f"Unsupported asset kind: {kind}")
