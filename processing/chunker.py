from dataclasses import dataclass, field
from typing import Any


@dataclass
class DocumentChunk:
    """A chunk of text with metadata."""

    text: str
    chunk_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


class DocumentChunker:
    """Split clinical trial and research paper text into smaller chunks."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")

        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(
        self,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> list[DocumentChunk]:
        """Split raw text into overlapping chunks."""

        if not text or not text.strip():
            return []

        text = " ".join(text.split())
        metadata = metadata or {}

        chunks: list[DocumentChunk] = []

        start = 0
        chunk_number = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))

            # Try to end at a natural boundary.
            if end < len(text):
                boundary = max(
                    text.rfind(". ", start, end),
                    text.rfind("? ", start, end),
                    text.rfind("! ", start, end),
                    text.rfind("\n", start, end),
                )

                if boundary > start + self.chunk_size // 2:
                    end = boundary + 1

            chunk = text[start:end].strip()

            if chunk:
                chunk_metadata = {
                    **metadata,
                    "chunk_number": chunk_number,
                    "start_position": start,
                    "end_position": end,
                }

                chunks.append(
                    DocumentChunk(
                        text=chunk,
                        chunk_id=f"chunk_{chunk_number}",
                        metadata=chunk_metadata,
                    )
                )

                chunk_number += 1

            next_start = end - self.chunk_overlap

            if next_start <= start:
                next_start = end

            start = next_start

        return chunks

    def chunk_document(
        self,
        text: str,
        document_id: str,
        document_type: str,
        metadata: dict[str, Any] | None = None,
    ) -> list[DocumentChunk]:
        """Chunk a document while attaching document metadata."""

        combined_metadata = {
            "document_id": document_id,
            "document_type": document_type,
            **(metadata or {}),
        }

        chunks = self.chunk_text(
            text=text,
            metadata=combined_metadata,
        )

        for chunk in chunks:
            chunk.chunk_id = f"{document_id}_{chunk.chunk_id}"

        return chunks

    def chunk_documents(
        self,
        documents: list[dict[str, Any]],
    ) -> list[DocumentChunk]:
        """Chunk multiple documents."""

        all_chunks: list[DocumentChunk] = []

        for document in documents:
            text = document.get("text", "")
            document_id = str(document.get("document_id", "unknown"))
            document_type = str(
                document.get("document_type", "unknown")
            )

            metadata = document.get("metadata", {})

            chunks = self.chunk_document(
                text=text,
                document_id=document_id,
                document_type=document_type,
                metadata=metadata,
            )

            all_chunks.extend(chunks)

        return all_chunks