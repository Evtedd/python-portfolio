import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Asset, AssetKind, AssetStatus, Segment
from app.vectorstore.math import cosine_similarity


class AssetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_asset(
        self,
        filename: str,
        kind: AssetKind,
        content_type: str,
        path: Path,
    ) -> Asset:
        asset = Asset(
            filename=filename,
            kind=kind.value,
            content_type=content_type,
            path=str(path),
            status=AssetStatus.pending.value,
        )
        self.session.add(asset)
        await self.session.commit()
        await self.session.refresh(asset)
        return asset

    async def get_asset(self, asset_id: int) -> Asset | None:
        return await self.session.get(Asset, asset_id)

    async def list_assets(self) -> list[Asset]:
        result = await self.session.execute(select(Asset).order_by(Asset.created_at.desc()))
        return list(result.scalars().all())

    async def next_pending(self) -> Asset | None:
        result = await self.session.execute(
            select(Asset)
            .where(Asset.status == AssetStatus.pending.value)
            .order_by(Asset.created_at)
            .limit(1),
        )
        return result.scalar_one_or_none()

    async def set_status(
        self,
        asset: Asset,
        status: AssetStatus,
        error: str | None = None,
    ) -> None:
        asset.status = status.value
        asset.error = error
        await self.session.commit()

    async def replace_segments(self, asset: Asset, segments: list[Segment]) -> None:
        loaded = await self.session.scalar(
            select(Asset).options(selectinload(Asset.segments)).where(Asset.id == asset.id),
        )
        if loaded is None:
            return
        loaded.segments.clear()
        loaded.segments.extend(segments)
        loaded.status = AssetStatus.ready.value
        loaded.error = None
        await self.session.commit()


class SearchRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def search(self, query_vector: list[float], top_k: int) -> list[tuple[Segment, float]]:
        result = await self.session.execute(
            select(Segment).options(selectinload(Segment.asset)),
        )
        scored: list[tuple[Segment, float]] = []
        for segment in result.scalars().all():
            vector = [float(value) for value in json.loads(segment.embedding)]
            score = cosine_similarity(query_vector, vector)
            if score > 0:
                scored.append((segment, score))
        return sorted(scored, key=lambda item: item[1], reverse=True)[:top_k]
