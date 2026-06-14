from dataclasses import dataclass

from app.models import AssetKind


@dataclass(frozen=True)
class ExtractedText:
    text: str
    page: int | None = None
    start_seconds: float | None = None
    end_seconds: float | None = None
    preview_path: str | None = None


EXTENSION_KIND = {
    ".pdf": AssetKind.pdf,
    ".mp3": AssetKind.audio,
    ".wav": AssetKind.audio,
    ".m4a": AssetKind.audio,
    ".mp4": AssetKind.video,
    ".mov": AssetKind.video,
    ".mkv": AssetKind.video,
    ".png": AssetKind.image,
    ".jpg": AssetKind.image,
    ".jpeg": AssetKind.image,
    ".webp": AssetKind.image,
}
