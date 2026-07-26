import sqlite3
import os
from pathlib import Path
from typing import Optional
from langgraph.checkpoint.sqlite import SqliteSaver
from kaizen.storage.paths import SESSIONS_DIR

# Global references
_connection: Optional[sqlite3.Connection] = None
_checkpointer: Optional[SqliteSaver] = None



def init_sqlite_db() -> sqlite3.Connection:
    """Initialize and open the SQLite database, ensuring tables are created.
    
    Returns:
        sqlite3.Connection: The opened SQLite database connection.
    """
    global _connection
    if _connection is not None:
        return _connection
        
    db_path = SESSIONS_DIR / "checkpoints.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Establish connection with check_same_thread=False for multi-threading safety
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    

    _connection = conn
    return conn

def get_sqlite_checkpointer() -> SqliteSaver:
    """Get or create the global SqliteSaver checkpointer instance.
    
    Returns:
        SqliteSaver: The SQLite checkpointer.
    """
    global _checkpointer, _connection
    if _checkpointer is not None:
        return _checkpointer
        
    if _connection is None:
        init_sqlite_db()
        

    checkpointer = SqliteSaver(_connection)
    
   
    checkpointer.setup()
    
    _checkpointer = checkpointer
    return checkpointer

def close_sqlite_db() -> None:
    """Close the database connection and reset global references."""
    global _connection, _checkpointer
    if _connection is not None:
        try:
            _connection.close()
        except Exception:
            pass
        _connection = None
    _checkpointer = None
