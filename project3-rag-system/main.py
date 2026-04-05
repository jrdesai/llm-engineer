# main.py
import shutil
from pathlib import Path

import psycopg2
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from config import DATABASE_URL
from ingestion import ingest_file
from retrieval import query_stream

app = FastAPI(
    title="RAG System",
    version="1.0.0",
)


# ── Request / Response models ─────────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str


# ── Endpoints ─────────────────────────────────────────────────────────────────


@app.get("/health")
def health():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.close()
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "ok", "database": "unreachable"}

# TODO 2: POST /ingest
# - Accept a file upload using: file: UploadFile = File(...)
# - Save it temporarily to /tmp/{file.filename} using shutil.copyfileobj
# - Call ingest_file(tmp_path) to run the pipeline
# - Return {"filename": file.filename, "chunks_stored": <number>}
# - Wrap in try/except, raise HTTPException(500) on failure
@app.post("/ingest")
def ingest(file: UploadFile = File(...)):
    try:
        tmp_path = f"/tmp/{file.filename}"
        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        chunks_stored = ingest_file(tmp_path)

        return {"filename": file.filename, "chunks_stored": chunks_stored}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# TODO 3: POST /query
# - Accept a QueryRequest body
# - Collect ALL chunks from query_stream() into a single string
#   Hint: "".join(chunk for chunk in query_stream(question))
# - Return {"question": question, "answer": answer}
# - Wrap in try/except, raise HTTPException(500) on failure
@app.post("/query")
def query(request: QueryRequest):
    try:
        answer = "".join(chunk for chunk in query_stream(request.question))
        return {"question": request.question, "answer": answer}
    except Exception as e:
        raise HTTPException(500, detail=str(e))


# TODO 4: POST /query/stream
# - Accept a QueryRequest body
# - Same streaming pattern as Project 2
# - Use StreamingResponse with media_type="text/plain"
# - Wrap the generator in try/except — yield error string on failure
@app.post("/query/stream")
def query_stream_endpoint(request: QueryRequest):
    def generate():
        try:
            yield from query_stream(request.question)
        except Exception as e:
            yield f"Error: {str(e)}"
    return StreamingResponse(generate(), media_type="text/plain")


# TODO 5: GET /documents
# - Connect to Postgres
# - Run: SELECT filename, COUNT(*) as chunks
#        FROM documents GROUP BY filename ORDER BY filename
# - Return list of {"filename": ..., "chunks": ...}
# - Wrap in try/except, raise HTTPException(500) on failure
@app.get("/documents")
def list_documents():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT filename, COUNT(*) as chunks
                    FROM documents
                    GROUP BY filename
                    ORDER BY filename
                    """
                )
                results = cursor.fetchall()
                return [{"filename": row[0], "chunks": row[1]} for row in results]
        finally:
            conn.close()
    except Exception as e:
        raise HTTPException(500, detail=str(e))