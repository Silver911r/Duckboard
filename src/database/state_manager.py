import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

class StateManager:
    """manages application state persistence using sqlite"""
    def __init__(self, db_path: Optional[str] = None):
        """init state manager
        args:
            db_path: path to sqlite db file. if none uses default location
        """
        if db_path is None:
            #store in user's home directory under .duckboard
            app_dir = Path.home() / ".duckboard"
            app_dir.mkdir(exist_ok=True)
            db_path = str(app_dir / "app_state.db")

        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row #enable column access by name
        self._init_database()

    def _init_database(self):
        """creates tables if they don't exist"""
        cursor = self.conn.cursor()

        #application settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )            
        """)

        #workspaces table (foundation for future feature)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workspaces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 0
            )            
        """)

        #data sources table (foundation for future feature)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id INTEGER NOT NULL,
                table_name TEXT NOT NULL,
                source_path TEXT NOT NULL,
                source_type TEXT NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
                UNIQUE(workspace_id, table_name)
            )            
        """)

        #query history table (foundation for future feature)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id INTEGER NOT NULL,
                query_text TEXT NOT NULL,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                execution_time_ms REAL,
                status TEXT,
                error_message TEXT,
                FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE
            )            
        """)

        self.conn.commit()

    #settings methods
    def set_setting(self, key: str, value: Any):
        """save a setting to the database"""
        cursor = self.conn.cursor()
        #workspaces table (foundation for future feature)
        cursor.execute("""
            INSERT OR REPLACE INTO app_settings (key, value, updated_at)
            VALUES (?,?,?)           
        """, (key, str(value), datetime.now()))
        self.conn.commit()

    def get_setting(self, key: str, default: Any = None) -> Optional[str]:
        """retrieve a setting from the database"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row['value'] if row else default
    
    def get_setting_int(self, key: str, default: int = 0) -> int:
        """retrieve an integer setting"""
        value = self.get_setting(key)
        return int(value) if value is not None else default
    
    def close(self):
        """close the database connection"""
        self.conn.close()