from typing import Any

from langchain_openai import OpenAIEmbeddings

from config.settings import settings
from processing.chunker import DocumentChunk


class Embedder:
    """Generate vector embeddings for document chunks."""

    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            api_key=settings.openai_api_key,
        )

    async def embed_text(self, text: str) -> list[float]:
        """Generate an embedding for a single text."""

        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        return await self.embeddings.aembed_query(text)

    async def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """Generate embeddings for multiple texts."""

        if not texts:
            return []

        return await self.embeddings.aembed_documents(texts)

    async def embed_chunks(
        self,
        chunks: list[DocumentChunk],
    ) -> list[dict[str, Any]]:
        """Generate embeddings for DocumentChunk objects."""

        if not chunks:
            return []

        texts = [chunk.text for chunk in chunks]

        vectors = await self.embed_documents(texts)

        results = []

        for chunk, vector in zip(chunks, vectors):
            results.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "text": chunk.text,
                    "embedding": vector,
                    "metadata": chunk.metadata,
                }
            )

        return results