from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from config.settings import settings
from processing.embedder import Embedder


class SemanticMemoryStore:
    """Store and retrieve long-term semantic memories using pgvector."""

    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or settings.database_url

        self.engine: AsyncEngine = create_async_engine(
            self.database_url,
            pool_pre_ping=True,
        )

        self.embedder = Embedder()

    async def initialize(self) -> None:
        """Create the pgvector extension and semantic memory table."""

        async with self.engine.begin() as connection:
            # Enable pgvector
            await connection.execute(
                text("CREATE EXTENSION IF NOT EXISTS vector")
            )

            # Create semantic memory table
            await connection.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS semantic_memory (
                        id SERIAL PRIMARY KEY,
                        memory_key TEXT UNIQUE NOT NULL,
                        content TEXT NOT NULL,
                        metadata JSONB DEFAULT '{}'::jsonb,
                        embedding vector(1536),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            )

    async def save(
        self,
        memory_key: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Save or update a semantic memory with its embedding."""

        if not memory_key.strip():
            raise ValueError("Memory key cannot be empty")

        if not content.strip():
            raise ValueError("Memory content cannot be empty")

        # Generate embedding for the memory
        embedding = await self.embedder.embed_text(content)

        async with self.engine.begin() as connection:
            await connection.execute(
                text(
                    """
                    INSERT INTO semantic_memory
                    (
                        memory_key,
                        content,
                        metadata,
                        embedding
                    )
                    VALUES
                    (
                        :memory_key,
                        :content,
                        CAST(:metadata AS JSONB),
                        CAST(:embedding AS vector)
                    )
                    ON CONFLICT (memory_key)
                    DO UPDATE SET
                        content = EXCLUDED.content,
                        metadata = EXCLUDED.metadata,
                        embedding = EXCLUDED.embedding,
                        updated_at = CURRENT_TIMESTAMP
                    """
                ),
                {
                    "memory_key": memory_key,
                    "content": content,
                    "metadata": self._json_string(metadata or {}),
                    "embedding": self._vector_string(embedding),
                },
            )

    async def get(
        self,
        memory_key: str,
    ) -> dict[str, Any] | None:
        """Retrieve a semantic memory by its key."""

        async with self.engine.connect() as connection:
            result = await connection.execute(
                text(
                    """
                    SELECT
                        id,
                        memory_key,
                        content,
                        metadata,
                        created_at,
                        updated_at
                    FROM semantic_memory
                    WHERE memory_key = :memory_key
                    """
                ),
                {
                    "memory_key": memory_key,
                },
            )

            row = result.mappings().first()

            if row is None:
                return None

            return dict(row)

    async def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Search semantic memories using vector similarity."""

        if not query.strip():
            return []

        if limit <= 0:
            return []

        # Convert query into an embedding
        query_embedding = await self.embedder.embed_text(query)

        async with self.engine.connect() as connection:
            result = await connection.execute(
                text(
                    """
                    SELECT
                        id,
                        memory_key,
                        content,
                        metadata,
                        created_at,
                        updated_at,
                        1 - (
                            embedding <=> CAST(:embedding AS vector)
                        ) AS similarity
                    FROM semantic_memory
                    WHERE embedding IS NOT NULL
                    ORDER BY embedding <=> CAST(:embedding AS vector)
                    LIMIT :limit
                    """
                ),
                {
                    "embedding": self._vector_string(query_embedding),
                    "limit": limit,
                },
            )

            rows = result.mappings().all()

            return [dict(row) for row in rows]

    async def delete(
        self,
        memory_key: str,
    ) -> bool:
        """Delete a semantic memory by key."""

        async with self.engine.begin() as connection:
            result = await connection.execute(
                text(
                    """
                    DELETE FROM semantic_memory
                    WHERE memory_key = :memory_key
                    """
                ),
                {
                    "memory_key": memory_key,
                },
            )

        return result.rowcount > 0

    async def close(self) -> None:
        """Close the database connection pool."""

        await self.engine.dispose()

    @staticmethod
    def _vector_string(vector: list[float]) -> str:
        """Convert a Python vector into pgvector format."""

        return "[" + ",".join(str(value) for value in vector) + "]"

    @staticmethod
    def _json_string(data: dict[str, Any]) -> str:
        """Convert dictionary to JSON string."""

        import json

        return json.dumps(data)