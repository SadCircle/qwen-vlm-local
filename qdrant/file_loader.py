import argparse
import asyncio
import re
from pathlib import Path
from typing import Iterable

from fastembed import TextEmbedding
from mcp_server_qdrant.embeddings.fastembed import FastEmbedProvider
from mcp_server_qdrant.qdrant import Entry, QdrantConnector


def list_input_files(input_dir: Path) -> list[Path]:
    return [path for path in input_dir.rglob("*") if path.is_file()]


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def tokenize_text(text: str) -> list[str]:
    return re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)


def split_into_chunks(
    text: str, chunk_size: int = 512, chunk_overlap: int = 64
) -> list[str]:
    tokens = tokenize_text(text)
    if not tokens:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk = " ".join(tokens[start:end])
        chunks.append(chunk)
        if end == len(tokens):
            break
        start = end - chunk_overlap
    return chunks


def build_embeddings_provider(model_path: str) -> FastEmbedProvider:
    return FastEmbedProvider(model_path)


def create_qdrant_connector(
    collection_name: str,
    model_path: str,
) -> QdrantConnector:
    provider = build_embeddings_provider(model_path)
    return QdrantConnector(
        qdrant_url="http://localhost:6333",
        qdrant_api_key=None,
        collection_name=collection_name,
        embedding_provider=provider,
    )


async def store_chunks(
    connector: QdrantConnector,
    chunks: Iterable[str],
    metadata: dict,
):
    for chunk in chunks:
        entry = Entry(content=chunk, metadata=metadata)
        await connector.store(entry)


async def main(
    input_dir: Path,
    collection_name: str,
    model_path: str,
    # qdrant_storage: str,
):
    connector = create_qdrant_connector(collection_name, model_path)

    files = list_input_files(input_dir)
    if not files:
        print(f"No files found in {input_dir}")
        return

    print(f"Found {len(files)} files in {input_dir}")

    for path in sorted(files):
        text = read_text_file(path)
        chunks = split_into_chunks(text)
        print(f"{path.relative_to(input_dir)}: {len(chunks)} chunks")
        await store_chunks(
            connector,
            chunks,
            metadata={"source_path": str(path), "file_name": path.name},
        )

    print(f"Finished storing files into collection '{collection_name}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Load files from ./input, tokenize and store embeddings into Qdrant"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("./input"),
        help="Directory with input files",
    )
    parser.add_argument(
        "--collection",
        type=str,
        default="test-collection",
        help="Qdrant collection name",
    )
    parser.add_argument(
        "--model-path",
        type=str,
        default="snowflake/snowflake-arctic-embed-l",
        help="Path to local FastEmbed model",
    )
    parser.add_argument(
        "--qdrant-storage",
        type=str,
        default="./qdrant_storage",
        help="Local Qdrant storage directory",
    )

    args = parser.parse_args()
    asyncio.run(
        main(
            input_dir=args.input_dir,
            collection_name=args.collection,
            model_path=args.model_path,
            # qdrant_storage=args.qdrant_storage,
        )
    )
