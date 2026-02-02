# Rheolwyr - Linux Text Expander
# Copyright (C) 2026 Chuck Talk <cwtalk1@gmail.com>
# Licensed under GPLv3 or later

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GObject
from .database import Database

class RheolwyrWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Rheolwyr")
        self.db = Database()
        self.current_snippet_id = None
        
        self.set_default_size(800, 600)
        
        # Main Layout
        self.split_view = Adw.OverlaySplitView()
        self.set_content(self.split_view)
        
        # Sidebar (Snippet List)
        self.sidebar_page = Adw.NavigationPage(title="Snippets", tag="sidebar")
        
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Toolbar for sidebar
        sidebar_header = Adw.HeaderBar(show_end_title_buttons=False)
        add_btn = Gtk.Button(icon_name="list-add-symbolic")
        add_btn.connect("clicked", self.on_add_clicked)
        sidebar_header.pack_start(add_btn)
        sidebar_box.append(sidebar_header)
        
        # ListBox for snippets
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.listbox.connect("row-selected", self.on_row_selected)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(self.listbox)
        scrolled.set_vexpand(True)
        sidebar_box.append(scrolled)
        
        self.sidebar_page.set_child(sidebar_box)
        self.split_view.set_sidebar(self.sidebar_page)
        self.split_view.set_min_sidebar_width(250)
        
        # Content (Editor)
        self.content_page = Adw.NavigationPage(title="Editor", tag="content")
        
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Toolbar for content
        content_header = Adw.HeaderBar()
        self.save_btn = Gtk.Button(label="Save")
        self.save_btn.add_css_class("suggested-action")
        self.save_btn.connect("clicked", self.on_save_clicked)
        self.save_btn.set_sensitive(False)
        content_header.pack_end(self.save_btn)
        
        self.delete_btn = Gtk.Button(icon_name="user-trash-symbolic")
        self.delete_btn.add_css_class("destructive-action")
        self.delete_btn.connect("clicked", self.on_delete_clicked)
        self.delete_btn.set_sensitive(False)
        content_header.pack_end(self.delete_btn)
        
        content_box.append(content_header)
        
        # Editor Fields
        form_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        form_box.set_margin_top(20)
        form_box.set_margin_bottom(20)
        form_box.set_margin_start(20)
        form_box.set_margin_end(20)
        
        # Name Entry
        self.name_entry = Adw.EntryRow(title="Snippet Name")
        form_box.append(self.name_entry)

        # Trigger Entry
        self.trigger_entry = Adw.EntryRow(title="Trigger Text (e.g. ;sig)")
        form_box.append(self.trigger_entry)
        
        # Content View
        editor_label = Gtk.Label(label="Snippet Content", xalign=0)
        editor_label.add_css_class("heading")
        form_box.append(editor_label)
        
        self.text_view = Gtk.TextView()
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.text_view.set_vexpand(True)
        self.text_buffer = self.text_view.get_buffer()
        
        editor_scroll = Gtk.ScrolledWindow()
        editor_scroll.set_child(self.text_view)
        editor_scroll.set_vexpand(True)
        editor_scroll.set_min_content_height(200)
        
        # Frame for editor to look nice
        frame = Gtk.Frame()
        frame.set_child(editor_scroll)
        form_box.append(frame)
        
        content_box.append(form_box)
        
        self.content_page.set_child(content_box)
        self.split_view.set_content(self.content_page)
        
        self.load_snippets()

    def load_snippets(self):
        # Clear existing
        while self.listbox.get_first_child():
            self.listbox.remove(self.listbox.get_first_child())
            
        snippets = self.db.get_all_snippets()
        row_to_select = None
        for s in snippets:
            # s: id, name, content, trigger
            row = Gtk.ListBoxRow()
            label = Gtk.Label(label=s[1], xalign=0, margin_start=10, margin_end=10, margin_top=10, margin_bottom=10)
            row.set_child(label)
            row.snippet_id = s[0]
            self.listbox.append(row)
            
            if self.current_snippet_id and row.snippet_id == self.current_snippet_id:
                row_to_select = row
        
        if row_to_select:
            self.listbox.select_row(row_to_select)

    def on_add_clicked(self, btn):
        self.current_snippet_id = None
        self.name_entry.set_text("New Snippet")
        self.trigger_entry.set_text("")
        self.text_buffer.set_text("")
        self.listbox.select_row(None)
        self.save_btn.set_sensitive(True)
        self.delete_btn.set_sensitive(False)
        self.name_entry.grab_focus()

    def on_row_selected(self, box, row):
        if row:
            self.current_snippet_id = row.snippet_id
            data = self.db.get_snippet_by_id(self.current_snippet_id)
            if data:
                self.name_entry.set_text(data[1])
                self.text_buffer.set_text(data[2])
                self.trigger_entry.set_text(data[3] if data[3] else "")
                self.save_btn.set_sensitive(True)
                self.delete_btn.set_sensitive(True)
        else:
            # Maybe clear fields if nothing selected?
            # But on_add_clicked handles specific clearing.
            pass

    def on_save_clicked(self, btn):
        name = self.name_entry.get_text()
        trigger = self.trigger_entry.get_text()
        start_iter = self.text_buffer.get_start_iter()
        end_iter = self.text_buffer.get_end_iter()
        content = self.text_buffer.get_text(start_iter, end_iter, True)
        
        # Basic validation
        if not name:
            # Minimal feedback: don't save if empty name
            return

        if self.current_snippet_id:
            self.db.update_snippet(self.current_snippet_id, name, content, trigger)
        else:
            self.current_snippet_id = self.db.add_snippet(name, content, trigger)
            
        self.load_snippets()
        
    def on_delete_clicked(self, btn):
        if self.current_snippet_id:
            self.db.delete_snippet(self.current_snippet_id)
            self.current_snippet_id = None
            self.name_entry.set_text("")
            self.trigger_entry.set_text("")
            self.text_buffer.set_text("")
            self.save_btn.set_sensitive(False)
            self.delete_btn.set_sensitive(False)
            self.load_snippets()
