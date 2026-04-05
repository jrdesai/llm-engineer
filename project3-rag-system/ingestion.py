# ingestion.py
import os
from pathlib import Path
from typing import List

import psycopg2
from dotenv import load_dotenv
from google import genai
from google.genai import types
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    DATABASE_URL, EMBEDDING_MODEL, EMBEDDING_DIMENSIONS,
    CHUNK_SIZE, CHUNK_OVERLAP
)

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def extract_text(file_path: str) -> str:
    """
    Read raw text from a file.
    Support .txt and .md for now — PDF support comes later.
    """
    return Path(file_path).read_text(encoding="utf-8")


def chunk_text(text: str) -> List[str]:
    """
    Split text into overlapping chunks using LangChain's text splitter.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    return splitter.split_text(text)


def embed_text(text: str) -> List[float]:
    """
    Convert text to a vector using Google's embedding model.
    Returns a list of 768 floats.
    """
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS)
    )
    return response.embeddings[0].values


def ingest_file(file_path: str) -> int:
    """
    Full ingestion pipeline: read → chunk → embed → store.
    Returns the number of chunks stored.
    """
    filename = Path(file_path).name

    text = extract_text(file_path)
    chunks = chunk_text(text)

    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cursor:
        for index, chunk in enumerate(chunks):
            embedding = embed_text(chunk)
            cursor.execute(
                "INSERT INTO documents (filename, chunk_text, embedding, chunk_index) VALUES (%s, %s, %s, %s)",
                (filename, chunk, str(embedding), index)
            )
    conn.commit()
    conn.close()
    return len(chunks)
