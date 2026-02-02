# Rheolwyr - Linux Text Expander
# Copyright (C) 2026 Chuck Talk <cwtalk1@gmail.com>
# Licensed under GPLv3 or later

import os
import sqlite3
from typing import List, Optional, Tuple
from gi.repository import GLib

class Database:
    def __init__(self, db_path: str = None):
        if db_path is None:
            data_dir = os.path.join(GLib.get_user_data_dir(), "rheolwyr")
            os.makedirs(data_dir, exist_ok=True)
            self.db_path = os.path.join(data_dir, "snippets.db")
        else:
            self.db_path = db_path
        self._init_db()

    def _init_db(self):
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
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO snippets (name, content, trigger) VALUES (?, ?, ?)",
                (name, content, trigger)
            )
            return cursor.lastrowid

    def update_snippet(self, snippet_id: int, name: str, content: str, trigger: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE snippets SET name = ?, content = ?, trigger = ? WHERE id = ?",
                (name, content, trigger, snippet_id)
            )

    def delete_snippet(self, snippet_id: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM snippets WHERE id = ?", (snippet_id,))

    def get_all_snippets(self) -> List[Tuple]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, content, trigger FROM snippets ORDER BY name")
            return cursor.fetchall()

    def get_snippet_by_id(self, snippet_id: int) -> Optional[Tuple]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, content, trigger FROM snippets WHERE id = ?", (snippet_id,))
            return cursor.fetchone()
