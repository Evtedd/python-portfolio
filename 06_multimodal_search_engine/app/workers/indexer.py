import asyncio
import json
import logging
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.chunking.text import chunk_words
from app.config import settings
from app.embeddings.providers import get_image_embeddings, get_text_embeddings
from app.ingestion.extractor import Extractor
from app.models import Asset, AssetKind, AssetStatus, Segment
from app.repository import AssetRepository
from app.transcription.provider import TranscriptionProvider

logger = logging.getLogger(__name__)


class Indexer:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = AssetRepository(session)
        self.extractor = Extractor(TranscriptionProvider())

    async def process_asset(self, asset: Asset) -> None:
        await self.repository.set_status(asset, AssetStatus.processing)
        try:
            kind = AssetKind(asset.kind)
            extracted = await self.extractor.extract(kind, Path(asset.path))
            if not extracted:
                raise ValueError("No content was extracted from asset")

            segments: list[Segment] = []
            for item in extracted:
                chunks = chunk_words(
                    item.text,
                    settings.chunk_words,
                    settings.chunk_overlap,
                    page=item.page,
                    start_seconds=item.start_seconds,
                    end_seconds=item.end_seconds,
                )
                for chunk in chunks:
                    provider = get_image_embeddings() if kind == AssetKind.image else get_text_embeddings()
                    vector = await provider.embed(chunk.text)
                    segments.append(
                        Segment(
                            asset_id=asset.id,
                            modality=kind.value,
                            text=chunk.text,
                            page=chunk.page,
                            start_seconds=chunk.start_seconds,
                            end_seconds=chunk.end_seconds,
                            preview_path=item.preview_path,
                            embedding=json.dumps(vector),
                        ),
                    )

            await self.repository.replace_segments(asset, segments)
        except Exception as exc:
            logger.exception("Asset indexing failed")
            await self.repository.set_status(asset, AssetStatus.failed, str(exc))


async def worker_loop(session_factory, stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        async with session_factory() as session:
            repository = AssetRepository(session)
            asset = await repository.next_pending()
            if asset is not None:
                await Indexer(session).process_asset(asset)

        try:
            await asyncio.wait_for(stop_event.wait(), settings.worker_poll_seconds)
        except TimeoutError:
            continue
