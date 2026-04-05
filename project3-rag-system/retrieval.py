# retrieval.py
import os
from pathlib import Path
from typing import Iterator

import psycopg2
from dotenv import load_dotenv
from google import genai
from google.genai import types
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from config import (
    DATABASE_URL, EMBEDDING_MODEL, EMBEDDING_DIMENSIONS,
    GEMINI_MODEL, LLM_TEMPERATURE, TOP_K_CHUNKS
)

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

SYSTEM_PROMPT = """You are a helpful assistant that answers questions
based strictly on the provided context chunks.

Rules:
- Only use information from the context provided
- If the answer is not in the context, say "I don't have enough
  information in the provided documents to answer this"
- Cite which part of the context supports your answer
- Be concise and direct"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", """Context chunks retrieved from documents:
{context}

Question: {question}

Answer based on the context above:""")
])


def embed_query(question: str) -> list[float]:
    """
    Embed the user's question using the same model used during ingestion.
    WHY same model? Vectors only make sense relative to each other
    within the same model's vector space.
    """
    response = client.models.embed_content(
        model = EMBEDDING_MODEL,
        contents = question,
        config = types.EmbedContentConfig(output_dimensionality = EMBEDDING_DIMENSIONS)
    )
    return response.embeddings[0].values


def retrieve_chunks(question: str) -> list[dict]:
    """
    Find the top K most relevant chunks for the question.
    Returns list of dicts with keys: filename, chunk_text, chunk_index
    """
    # TODO 2: embed the question using embed_query()
    # TODO 3: connect to Postgres
    # TODO 4: run this similarity search query:
    #   SELECT filename, chunk_text, chunk_index
    #   FROM documents
    #   ORDER BY embedding <-> %s   ← cosine distance operator
    #   LIMIT %s
    # Pass: (str(query_vector), TOP_K_CHUNKS)
    # TODO 5: return results as list of dicts
    # Hint: cursor.fetchall() returns list of tuples
    # Convert each tuple to: {"filename": row[0], "chunk_text": row[1], "chunk_index": row[2]}
    query_vector = embed_query(question)
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT filename, chunk_text, chunk_index
                FROM documents
                ORDER BY embedding <-> %s
                LIMIT %s
                """,
                (str(query_vector), TOP_K_CHUNKS)
            )
            results = cursor.fetchall()
            return [{"filename": row[0], "chunk_text": row[1], "chunk_index": row[2]} for row in results]
    finally:
        conn.close()



def format_context(chunks: list[dict]) -> str:
    """
    Format retrieved chunks into a readable context string for the LLM.
    """
    # TODO 6: format each chunk like this:
    # [Source: filename, chunk 0]
    # chunk_text
    #
    # [Source: filename, chunk 1]
    # chunk_text
    parts = []
    for chunk in chunks:
        parts.append(f"[Source: {chunk['filename']}, chunk {chunk['chunk_index']}]\n{chunk['chunk_text']}")

    # Join all parts with a blank line between them
    return "\n\n".join(parts)



def query_stream(question: str) -> Iterator[str]:
    """
    Full RAG pipeline: embed → retrieve → generate (streaming).
    """
    # TODO 7: call retrieve_chunks() to get relevant chunks
    # TODO 8: call format_context() to format them
    # TODO 9: build the LangChain chain:
    #   llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=LLM_TEMPERATURE,
    #                                google_api_key=os.getenv("GOOGLE_API_KEY"))
    #   chain = prompt | llm | StrOutputParser()
    # TODO 10: yield from chain.stream({"context": context, "question": question})
    chunks = retrieve_chunks(question)
    context = format_context(chunks)
    llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=LLM_TEMPERATURE, google_api_key=os.getenv("GOOGLE_API_KEY"))
    chain = prompt | llm | StrOutputParser()
    yield from chain.stream({"context": context, "question": question})
