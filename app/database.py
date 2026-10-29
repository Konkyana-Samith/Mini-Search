
import sqlite3
from pathlib import Path


class Database:
    def __init__(self, db_path: str = "data/minisearch.db"):
        self.db_path = Path(db_path)

    def initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def add_document(self, document_id: int, title: str, content: str) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT INTO documents (id, title, content)
                VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    content = excluded.content
                """,
                (document_id, title, content),
            )
    
    def get_document(self, document_id: int) -> dict | None:
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                """
                SELECT id, title, content, created_at
                FROM documents
                WHERE id = ?
                """,
                (document_id,),
            ).fetchone()

        return dict(row) if row else None

    def get_all_documents(self) -> list[dict]:
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT id, title, content, created_at
                FROM documents
                ORDER BY id
                """
            ).fetchall()

        return [dict(row) for row in rows]
    
    def delete_document(self, document_id: int) -> bool:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.execute(
                "DELETE FROM documents WHERE id = ?",
                (document_id,),
            )
            return cursor.rowcount > 0
