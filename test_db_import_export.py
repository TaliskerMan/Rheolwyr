import os
import json
from rheolwyr.database import Database

def test_import_export():
    db_path = "test_snippets.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    db = Database(db_path)
    db.add_snippet("Test1", "Content1", ";t1")
    db.add_snippet("Test2", "Content2", ";t2")
    
    export_path = "exported.json"
    success = db.export_snippets(export_path)
    if not success:
        print("Export failed")
        return
    
    with open(export_path, 'r') as f:
        data = json.load(f)
        if len(data) != 2:
            print(f"Exported data has wrong length: {len(data)}")
            return
            
    # Test Import
    db2 = Database("test_snippets2.db")
    count = db2.import_snippets(export_path)
    if count != 2:
        print(f"Import failed, count: {count}")
        return
        
    snippets = db2.get_all_snippets()
    if len(snippets) != 2:
        print("Imported DB has wrong number of snippets")
        return
        
    print("Import/Export mechanism works properly!")
    
    # Cleanup
    os.remove("test_snippets.db")
    os.remove("test_snippets2.db")
    os.remove("exported.json")

test_import_export()
