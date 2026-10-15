import json
import numpy as np
import psycopg
from psycopg.rows import dict_row
from pgvector.psycopg import register_vector
from .config import settings
from .embeddings import embed, model_id


def connect():
    connection = psycopg.connect(settings.database_dsn, connect_timeout=5, row_factory=dict_row)
    register_vector(connection)
    return connection

def chunks(text: str, size: int = 180, overlap: int = 30) -> list[str]:
    words = text.split()
    return [" ".join(words[i:i+size]) for i in range(0, len(words), size-overlap)]

def ingest(book: dict) -> dict:
    parts = chunks(book["content"])
    # Compute all embeddings before changing persisted chunks.
    vectors = [embed(book["title"] + " " + p) for p in parts]
    with connect() as db:
        db.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (book["id"],))
        db.execute("""INSERT INTO runbooks(id,service,title,content,action,risk) VALUES (%s,%s,%s,%s,%s,%s)
            ON CONFLICT(id) DO UPDATE SET service=excluded.service,title=excluded.title,content=excluded.content,action=excluded.action,risk=excluded.risk""",
            (book["id"],book["service"],book["title"],book["content"],book.get("action","manual_review"),book.get("risk","HIGH")))
        db.execute("DELETE FROM runbook_chunks WHERE runbook_id=%s", (book["id"],))
        for i, (part, vector) in enumerate(zip(parts, vectors)):
            db.execute("INSERT INTO runbook_chunks(id,runbook_id,content,embedding,embedding_model) VALUES (%s,%s,%s,%s,%s)",
                (f'{book["id"]}:{i}', book["id"], part, np.array(vector), model_id()))
    return {"id":book["id"], "chunks":len(parts), "embedding_model":model_id()}

def seed() -> None:
    books = json.loads((settings.fixtures_dir / "runbooks.json").read_text())
    for book in books:
        with connect() as db:
            existing = db.execute("SELECT count(*) AS n FROM runbook_chunks WHERE runbook_id=%s AND embedding_model=%s",(book["id"],model_id())).fetchone()["n"]
        if not existing:
            ingest(book)

def retrieve(service: str, query: str, limit: int = 3) -> list[dict]:
    vector = np.array(embed(query))
    with connect() as db:
        return db.execute("""SELECT c.id AS chunk_id, c.runbook_id, r.title, c.content,
            1 - (c.embedding <=> %s) AS score
            FROM runbook_chunks c JOIN runbooks r ON r.id=c.runbook_id
            WHERE r.service=%s AND c.embedding_model=%s
            ORDER BY c.embedding <=> %s, c.id LIMIT %s""",(vector,service,model_id(),vector,limit)).fetchall()

def list_runbooks() -> list[dict]:
    with connect() as db:
        return db.execute("SELECT id,service,title,content,action,risk FROM runbooks ORDER BY id").fetchall()
