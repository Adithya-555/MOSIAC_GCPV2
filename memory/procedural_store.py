from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from config.settings import settings


class ProceduralMemoryStore:
    """Store reusable procedures, rules, and workflows."""

    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or settings.database_url

        self.engine: AsyncEngine = create_async_engine(
            self.database_url,
            pool_pre_ping=True,
        )

    async def initialize(self) -> None:
        """Create the procedural memory table."""

        async with self.engine.begin() as connection:
            await connection.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS procedural_memory (
                        id SERIAL PRIMARY KEY,
                        procedure_name TEXT UNIQUE NOT NULL,
                        instructions TEXT NOT NULL,
                        metadata JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            )

    async def save(
        self,
        procedure_name: str,
        instructions: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Save or update a reusable procedure."""

        if not procedure_name.strip():
            raise ValueError("Procedure name cannot be empty")

        if not instructions.strip():
            raise ValueError("Procedure instructions cannot be empty")

        async with self.engine.begin() as connection:
            await connection.execute(
                text(
                    """
                    INSERT INTO procedural_memory
                    (
                        procedure_name,
                        instructions,
                        metadata
                    )
                    VALUES
                    (
                        :procedure_name,
                        :instructions,
                        CAST(:metadata AS JSONB)
                    )
                    ON CONFLICT (procedure_name)
                    DO UPDATE SET
                        instructions = EXCLUDED.instructions,
                        metadata = EXCLUDED.metadata,
                        updated_at = CURRENT_TIMESTAMP
                    """
                ),
                {
                    "procedure_name": procedure_name,
                    "instructions": instructions,
                    "metadata": self._json_string(metadata or {}),
                },
            )

    async def get(
        self,
        procedure_name: str,
    ) -> dict[str, Any] | None:
        """Retrieve a procedure by name."""

        async with self.engine.connect() as connection:
            result = await connection.execute(
                text(
                    """
                    SELECT
                        id,
                        procedure_name,
                        instructions,
                        metadata,
                        created_at,
                        updated_at
                    FROM procedural_memory
                    WHERE procedure_name = :procedure_name
                    """
                ),
                {
                    "procedure_name": procedure_name,
                },
            )

            row = result.mappings().first()

            if row is None:
                return None

            return dict(row)

    async def list_all(
        self,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Return stored procedures."""

        if limit <= 0:
            return []

        async with self.engine.connect() as connection:
            result = await connection.execute(
                text(
                    """
                    SELECT
                        id,
                        procedure_name,
                        instructions,
                        metadata,
                        created_at,
                        updated_at
                    FROM procedural_memory
                    ORDER BY updated_at DESC
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
        procedure_name: str,
    ) -> bool:
        """Delete a procedure by name."""

        async with self.engine.begin() as connection:
            result = await connection.execute(
                text(
                    """
                    DELETE FROM procedural_memory
                    WHERE procedure_name = :procedure_name
                    """
                ),
                {
                    "procedure_name": procedure_name,
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