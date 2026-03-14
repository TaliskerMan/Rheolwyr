import os
import sqlite3
import json
from typing import List, Optional, Tuple
from gi.repository import GLib

def apply_patch():
    file_path = "/home/freecode/antigrav/Rheolwyr/src/rheolwyr/database.py"
    with open(file_path, "r") as f:
        content = f.read()

    patch = """
    def export_snippets(self, filepath: str) -> bool:
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
        except Exception as e:
            print(f"Error exporting snippets: {e}")
            return False

    def import_snippets(self, filepath: str) -> int:
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
        except Exception as e:
            print(f"Error importing snippets: {e}")
            return -1
"""
    
    if "def export_snippets" not in content:
        content += patch
        with open(file_path, "w") as f:
            f.write(content)
        print("Patched database.py")
    else:
        print("Database already patched.")

apply_patch()
