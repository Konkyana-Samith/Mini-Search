
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from pydantic import BaseModel, Field

from app.database import Database
from app.search_engine import SearchEngine

from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


_SNIPPET_LENGTH = 200


class DocumentCreate(BaseModel):
    id: int
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)


def _make_snippet(content: str, max_length: int = _SNIPPET_LENGTH) -> str:
    """Return a plain-text excerpt of *content* suitable for display."""
    text = content.strip()
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + "…"


def create_app(db_path: str | Path = "data/minisearch.db") -> FastAPI:

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        database = Database(db_path)
        database.initialize()
        engine = SearchEngine(database)

        app.state.database = database
        app.state.engine = engine

        yield

    app = FastAPI(
        title="MiniSearch API",
        description="A lightweight information retrieval search engine",
        version="0.1.0",
        lifespan=lifespan,
    )

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    @app.post("/documents", status_code=201)
    def create_document(document: DocumentCreate, request: Request):
        engine = request.app.state.engine
        engine.add_document(
            document_id=document.id,
            title=document.title,
            content=document.content,
        )
        return {
            "message": "Document added successfully",
            "id": document.id,
            "title": document.title,
        }

    @app.get("/documents")
    def list_documents(request: Request):
        """Return all documents stored in the database."""
        database = request.app.state.database
        docs = database.get_all_documents()
        return {
            "count": len(docs),
            "documents": docs,
        }

    @app.get("/search")
    def search_documents(
        request: Request,
        q: str = Query(min_length=1),
        k: int = Query(default=10, ge=1, le=100),
    ):
        engine = request.app.state.engine
        results = engine.search(q, k=k)
        return {
            "query": q,
            "count": len(results),
            "results": [
                {
                    "id": document_id,
                    "title": engine.documents[document_id]["title"],
                    "snippet": _make_snippet(
                        engine.documents[document_id]["content"]
                    ),
                    "score": score,
                }
                for score, document_id in results
            ],
        }

    @app.get("/documents/{document_id}")
    def get_document(document_id: int, request: Request):
        document = request.app.state.database.get_document(document_id)
        if document is None:
            raise HTTPException(status_code=404, detail="Document not found")
        return document

    @app.delete("/documents/{document_id}")
    def delete_document(document_id: int, request: Request):
        deleted = request.app.state.engine.delete_document(document_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Document not found")
        return {
            "message": "Document deleted successfully",
            "id": document_id,
        }

    static_dir = Path(__file__).resolve().parent.parent / "static"

    app.mount(
        "/static",
        StaticFiles(directory=static_dir),
        name="static",
    )

    @app.get("/", include_in_schema=False)
    def dashboard():
        return FileResponse(static_dir / "index.html")

    return app


app = create_app()
