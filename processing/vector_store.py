from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from config.settings import settings


class VectorStore:
    """PostgreSQL + pgvector storage for document embeddings."""

    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or settings.database_url
        self.engine: AsyncEngine = create_async_engine(
            self.database_url,
            pool_pre_ping=True,
        )

    async def initialize(self) -> None:
        """Create the pgvector extension and chunks table."""

        async with self.engine.begin() as connection:
            await connection.execute(
                text("CREATE EXTENSION IF NOT EXISTS vector")
            )

            await connection.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS document_chunks (
                        id SERIAL PRIMARY KEY,
                        chunk_id TEXT UNIQUE NOT NULL,
                        text TEXT NOT NULL,
                        document_id TEXT,
                        document_type TEXT,
                        metadata JSONB DEFAULT '{}'::jsonb,
                        embedding vector(1536),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            )

    async def add_chunks(
        self,
        chunks: list[dict[str, Any]],
    ) -> int:
        """Store chunks and their embeddings."""

        if not chunks:
            return 0

        async with self.engine.begin() as connection:
            for chunk in chunks:
                metadata = chunk.get("metadata", {})

                await connection.execute(
                    text(
                        """
                        INSERT INTO document_chunks
                        (
                            chunk_id,
                            text,
                            document_id,
                            document_type,
                            metadata,
                            embedding
                        )
                        VALUES
                        (
                            :chunk_id,
                            :text,
                            :document_id,
                            :document_type,
                            CAST(:metadata AS JSONB),
                            CAST(:embedding AS vector)
                        )
                        ON CONFLICT (chunk_id)
                        DO UPDATE SET
                            text = EXCLUDED.text,
                            metadata = EXCLUDED.metadata,
                            embedding = EXCLUDED.embedding
                        """
                    ),
                    {
                        "chunk_id": chunk["chunk_id"],
                        "text": chunk["text"],
                        "document_id": metadata.get("document_id"),
                        "document_type": metadata.get("document_type"),
                        "metadata": self._json_string(metadata),
                        "embedding": self._vector_string(
                            chunk["embedding"]
                        ),
                    },
                )

        return len(chunks)

    async def similarity_search(
        self,
        embedding: list[float],
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Find the most similar document chunks."""

        if not embedding:
            return []

        async with self.engine.connect() as connection:
            result = await connection.execute(
                text(
                    """
                    SELECT
                        chunk_id,
                        text,
                        document_id,
                        document_type,
                        metadata,
                        1 - (embedding <=> CAST(:embedding AS vector))
                            AS similarity
                    FROM document_chunks
                    WHERE embedding IS NOT NULL
                    ORDER BY embedding <=> CAST(:embedding AS vector)
                    LIMIT :limit
                    """
                ),
                {
                    "embedding": self._vector_string(embedding),
                    "limit": limit,
                },
            )

            rows = result.mappings().all()

            return [dict(row) for row in rows]

    async def delete_chunk(self, chunk_id: str) -> bool:
        """Delete a chunk by ID."""

        async with self.engine.begin() as connection:
            result = await connection.execute(
                text(
                    """
                    DELETE FROM document_chunks
                    WHERE chunk_id = :chunk_id
                    """
                ),
                {"chunk_id": chunk_id},
            )

        return result.rowcount > 0

    async def close(self) -> None:
        """Close the database connection pool."""

        await self.engine.dispose()

    @staticmethod
    def _vector_string(vector: list[float]) -> str:
        return "[" + ",".join(str(value) for value in vector) + "]"

    @staticmethod
    def _json_string(data: dict[str, Any]) -> str:
        import json

        return json.dumps(data)