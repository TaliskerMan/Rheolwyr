import os
import sys

file_path = "/home/freecode/antigrav/Rheolwyr/src/rheolwyr/window.py"
with open(file_path, "r") as f:
    orig = f.read()

# 1. Add json to imports
# Wait, actually python patch script is easier using string replacement
orig = orig.replace(
    "import importlib.metadata\nimport gi\n",
    "import importlib.metadata\nimport json\nimport gi\n"
)

# 2. Add menu options
menu_addition = """
        section_main = Gio.Menu()
        section_main.append("Import Snippets", "win.import-snippets")
        section_main.append("Export Snippets", "win.export-snippets")
        section_main.append("Instructions", "win.instructions")
        theme_menu.append_section(None, section_main)
        
        section = Gio.Menu()
"""
orig = orig.replace("        section = Gio.Menu()\n", menu_addition)

# 3. Add Gio actions
actions_addition = """
        action_import = Gio.SimpleAction.new("import-snippets", None)
        action_import.connect("activate", self.on_import_action)
        self.add_action(action_import)
        
        action_export = Gio.SimpleAction.new("export-snippets", None)
        action_export.connect("activate", self.on_export_action)
        self.add_action(action_export)

        action_instructions = Gio.SimpleAction.new("instructions", None)
        action_instructions.connect("activate", self.on_instructions_action)
        self.add_action(action_instructions)
        
        action_about = Gio.SimpleAction.new("about", None)
"""
orig = orig.replace('        action_about = Gio.SimpleAction.new("about", None)\n', actions_addition)

# 4. Add the methods at the end of the class
methods_addition = """
    def on_instructions_action(self, action, param):
        instructions_text = \"\"\"
<b>Welcome to Rheolwyr!</b>

Rheolwyr is a Linux text expansion tool that runs in the background.

<b>How to Use:</b>
1. Create a "Snippet" by clicking the '+' button.
2. Enter a Name for your snippet.
3. Enter a <b>Trigger Text</b>. This is the sequence of characters you type to trigger the expansion (e.g., ;email).
4. Enter the <b>Snippet Content</b>. This is the text that will replace your trigger.
5. Click Save.

Once saved, whenever you type the Trigger Text in any text field across your system, it will be automatically replaced with the Snippet Content!

<b>Import/Export:</b>
Use the menu to export your snippets to a JSON file for backup, or import snippets from a previously saved JSON file.
\"\"\"
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading="Rheolwyr Instructions",
            body=instructions_text
        )
        dialog.set_body_use_markup(True)
        dialog.add_response("ok", "Got it!")
        dialog.present()

    def on_import_action(self, action, param):
        dialog = Gtk.FileDialog()
        dialog.set_title("Import Snippets")
        
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filter_json = Gtk.FileFilter()
        filter_json.set_name("JSON Files")
        filter_json.add_mime_type("application/json")
        filter_json.add_pattern("*.json")
        filters.append(filter_json)
        dialog.set_filters(filters)
        
        dialog.open(self, None, self.on_import_dialog_open_cb)

    def on_import_dialog_open_cb(self, dialog, result):
        try:
            file = dialog.open_finish(result)
            if file:
                path = file.get_path()
                count = self.db.import_snippets(path)
                if count >= 0:
                    self.load_snippets()
                    self.show_error_dialog(f"Successfully imported {count} snippets.")
                else:
                    self.show_error_dialog("Failed to import snippets. Check file format.")
        except gi.repository.GLib.GError as e:
            pass # User cancelled or similar

    def on_export_action(self, action, param):
        dialog = Gtk.FileDialog()
        dialog.set_title("Export Snippets")
        dialog.set_initial_name("rheolwyr_snippets.json")
        
        dialog.save(self, None, self.on_export_dialog_save_cb)

    def on_export_dialog_save_cb(self, dialog, result):
        try:
            file = dialog.save_finish(result)
            if file:
                path = file.get_path()
                if not path.endswith('.json'):
                    path += '.json'
                success = self.db.export_snippets(path)
                if success:
                    self.show_error_dialog("Snippets exported successfully.")
                else:
                    self.show_error_dialog("Failed to export snippets.")
        except gi.repository.GLib.GError as e:
            pass # User cancelled
"""
orig = orig + methods_addition

with open(file_path, "w") as f:
    f.write(orig)

print("Patched window.py")
