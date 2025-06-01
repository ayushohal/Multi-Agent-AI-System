import sqlite3
import os
from datetime import datetime
from typing import Optional, Any, List, Tuple
class SharedMemory:
    def __init__(self, db_path: str = "shared_memory/memory.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.create_table()
    def create_table(self) -> None:
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS memory_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                source TEXT,
                format TEXT,
                intent TEXT,
                extracted_values TEXT,
                thread_id TEXT
            )
        ''')
        self.conn.commit()
    def log_entry(
        self,
        source: str,
        format: str,
        intent: str,
        extracted_values: Optional[Any] = None,
        thread_id: Optional[str] = None
    ) -> None:
        """Log a new entry into the shared memory."""
        timestamp = datetime.utcnow().isoformat()
        self.conn.execute('''
            INSERT INTO memory_log (timestamp, source, format, intent, extracted_values, thread_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, source, format, intent, str(extracted_values), thread_id))
        self.conn.commit()
    def get_all_logs(self) -> List[Tuple]:
        """Retrieve all memory log entries."""
        cursor = self.conn.execute("SELECT * FROM memory_log")
        return cursor.fetchall()
    def close(self) -> None:
        """Close the database connection."""
        self.conn.close()
    def __enter__(self) -> "SharedMemory":
        return self
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

