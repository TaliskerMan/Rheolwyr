# Rheolwyr - Linux Text Expander
# Copyright (C) 2026 Chuck Talk <chuck@nordheim.online>
# Licensed under GPLv3 or later

import os
import sqlite3
from typing import List, Optional, Tuple

from gi.repository import GLib

"""
Database Access Provider Module.

Manages snippet entries, triggers, shortcuts, and content using an SQLite3 database backend.
"""

class Database:
    """
    Handler for SQLite database operations related to Rheolwyr snippets.
    """
    def __init__(self, db_path: str = None):
        """
        Initialize the database connection.
        
        Creates the database and schema under user local data if no custom path is given.
        """
        if db_path is None:
            data_dir = os.path.join(GLib.get_user_data_dir(), "rheolwyr")
            os.makedirs(data_dir, exist_ok=True)
            self.db_path = os.path.join(data_dir, "snippets.db")
        else:
            self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """
        Create the target snippets table if it does not already exist.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS snippets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    trigger TEXT,
                    shortcut TEXT,
                    content TEXT NOT NULL
                )
            """)
            conn.commit()

    def add_snippet(self, name: str, content: str, trigger: str = "") -> int:
        """
        Insert a new snippet into the database and return its auto-incremented ID.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO snippets (name, content, trigger) VALUES (?, ?, ?)",
                (name, content, trigger)
            )
            return cursor.lastrowid

    def update_snippet(self, snippet_id: int, name: str, content: str, trigger: str):
        """
        Update fields of a pre-existing snippet matching the given ID.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE snippets SET name = ?, content = ?, trigger = ? WHERE id = ?",
                (name, content, trigger, snippet_id)
            )

    def delete_snippet(self, snippet_id: int):
        """
        Remove a snippet matching the given ID from database records.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM snippets WHERE id = ?", (snippet_id,))

    def get_all_snippets(self) -> List[Tuple]:
        """
        Retrieve all stored snippets ordered alphabetically by name.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, content, trigger FROM snippets ORDER BY name")
            return cursor.fetchall()

    def get_snippet_by_id(self, snippet_id: int) -> Optional[Tuple]:
        """
        Retrieve a single snippet matching the given ID.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, content, trigger FROM snippets WHERE id = ?", (snippet_id,))
            return cursor.fetchone()

    def export_snippets(self, filepath: str) -> bool:
        """
        Serialize all database snippets into a JSON formatted file.
        """
        try:
            snippets = self.get_all_snippets()
            data = []
            for s in snippets:
                # s: id, name, content, trigger
                data.append({
                    "name": s[1],
                    "content": s[2],
                    "trigger": s[3] if s[3] else ""
                })
            import json
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as exception:
            print(f"Error exporting snippets: {exception}")
            return False

    def import_snippets(self, filepath: str) -> int:
        """
        Parse and import whitelisted snippets from a JSON file.
        
        Validates content and filters out duplicate records. Returns imported counts.
        """
        imported_count = 0
        try:
            import json
            with open(filepath, 'r') as f:
                data = json.load(f)

            existing = self.get_all_snippets()
            # Create a set of (name, content, trigger) for quick dedup
            existing_set = {(s[1], s[2], s[3] if s[3] else "") for s in existing}

            for item in data:
                name = item.get("name")
                content = item.get("content")
                trigger = item.get("trigger", "")

                if not name or not content:
                    continue

                if (name, content, trigger) not in existing_set:
                    self.add_snippet(name, content, trigger)
                    imported_count += 1
            return imported_count
        except Exception as exception:
            print(f"Error importing snippets: {exception}")
            return -1
