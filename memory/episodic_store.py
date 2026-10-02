from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from config.settings import settings


class EpisodicMemoryStore:
    """Store and retrieve past system events and interactions."""

    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or settings.database_url

        self.engine: AsyncEngine = create_async_engine(
            self.database_url,
            pool_pre_ping=True,
        )

    async def initialize(self) -> None:
        """Create the episodic memory table."""

        async with self.engine.begin() as connection:
            await connection.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS episodic_memory (
                        id SERIAL PRIMARY KEY,
                        event_type TEXT NOT NULL,
                        description TEXT NOT NULL,
                        metadata JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            )

    async def save(
        self,
        event_type: str,
        description: str,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        """Save an event and return its database ID."""

        if not event_type.strip():
            raise ValueError("Event type cannot be empty")

        if not description.strip():
            raise ValueError("Event description cannot be empty")

        async with self.engine.begin() as connection:
            result = await connection.execute(
                text(
                    """
                    INSERT INTO episodic_memory
                    (
                        event_type,
                        description,
                        metadata
                    )
                    VALUES
                    (
                        :event_type,
                        :description,
                        CAST(:metadata AS JSONB)
                    )
                    RETURNING id
                    """
                ),
                {
                    "event_type": event_type,
                    "description": description,
                    "metadata": self._json_string(metadata or {}),
                },
            )

            return result.scalar_one()

    async def get(
        self,
        event_id: int,
    ) -> dict[str, Any] | None:
        """Retrieve a specific event by ID."""

        async with self.engine.connect() as connection:
            result = await connection.execute(
                text(
                    """
                    SELECT
                        id,
                        event_type,
                        description,
                        metadata,
                        created_at
                    FROM episodic_memory
                    WHERE id = :event_id
                    """
                ),
                {
                    "event_id": event_id,
                },
            )

            row = result.mappings().first()

            if row is None:
                return None

            return dict(row)

    async def get_recent(
        self,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Get the most recent events."""

        if limit <= 0:
            return []

        async with self.engine.connect() as connection:
            result = await connection.execute(
                text(
                    """
                    SELECT
                        id,
                        event_type,
                        description,
                        metadata,
                        created_at
                    FROM episodic_memory
                    ORDER BY created_at DESC
                    LIMIT :limit
                    """
                ),
                {
                    "limit": limit,
                },
            )

            rows = result.mappings().all()

            return [dict(row) for row in rows]

    async def search(
        self,
        event_type: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Search previous events by event type."""

        if limit <= 0:
            return []

        async with self.engine.connect() as connection:

            if event_type and event_type.strip():
                result = await connection.execute(
                    text(
                        """
                        SELECT
                            id,
                            event_type,
                            description,
                            metadata,
                            created_at
                        FROM episodic_memory
                        WHERE event_type = :event_type
                        ORDER BY created_at DESC
                        LIMIT :limit
                        """
                    ),
                    {
                        "event_type": event_type,
                        "limit": limit,
                    },
                )

            else:
                result = await connection.execute(
                    text(
                        """
                        SELECT
                            id,
                            event_type,
                            description,
                            metadata,
                            created_at
                        FROM episodic_memory
                        ORDER BY created_at DESC
                        LIMIT :limit
                        """
                    ),
                    {
                        "limit": limit,
                    },
                )

            rows = result.mappings().all()

            return [dict(row) for row in rows]

    async def delete(
        self,
        event_id: int,
    ) -> bool:
        """Delete an event by ID."""

        async with self.engine.begin() as connection:
            result = await connection.execute(
                text(
                    """
                    DELETE FROM episodic_memory
                    WHERE id = :event_id
                    """
                ),
                {
                    "event_id": event_id,
                },
            )

        return result.rowcount > 0

    async def close(self) -> None:
        """Close the database connection pool."""

        await self.engine.dispose()

    @staticmethod
    def _json_string(data: dict[str, Any]) -> str:
        """Convert a dictionary into a JSON string."""

        import json

        return json.dumps(data)