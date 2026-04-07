import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

import os
import json
from terminatorlib.plugin import Plugin

PLUGIN_NAME = 'SnipBox'
AVAILABLE = ['SnipBoxPlugin']

class SnipBoxPlugin(Plugin):
    capabilities = ['terminal_menu']

    def __init__(self):
        Plugin.__init__(self)
        self.snippets = {}
        self.load_snippets()

    def load_snippets(self):
        """Load snippets from configuration file"""
        config_path = os.path.expanduser('~/.config/terminator/snippets.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.snippets = json.load(f)
            except Exception as e:
                print(f"Error loading snippets: {e}")
                self.snippets = {}
        else:
            # Create default configuration file
            self.create_default_config()

    def create_default_config(self):
        """Create a default configuration file"""
        config_dir = os.path.expanduser('~/.config/terminator')
        config_path = os.path.join(config_dir, 'snippets.json')

        default_snippets = {
            "Examples": {
                "list directory": "ls -la",
                "clear screen": "clear",
                "check ip": "ip addr show"
            }
        }

        try:
            os.makedirs(config_dir, exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_snippets, f, indent=2, ensure_ascii=False)
            self.snippets = default_snippets
        except Exception as e:
            print(f"Error creating configuration: {e}")

    def callback(self, menuitems, menu, terminal):
        """Create context menu with snippets"""
        # Option to manage snippets
        manage_item = Gtk.MenuItem(label='Manage Snippets')
        manage_item.connect('activate', self.show_manager, terminal)
        menuitems.append(manage_item)

        menuitems.append(Gtk.SeparatorMenuItem())

        # Add snippets to menu
        for category, snippets in self.snippets.items():
            if isinstance(snippets, dict):
                submenu = Gtk.Menu()
                for name, command in snippets.items():
                    item = Gtk.MenuItem(label=name)
                    item.connect('activate', self.execute_snippet, terminal, command)
                    submenu.append(item)

                category_item = Gtk.MenuItem(label=category)
                category_item.set_submenu(submenu)
                menuitems.append(category_item)

    def execute_snippet(self, widget, terminal, command):
        """Execute snippet in the terminal"""
        if terminal and hasattr(terminal, 'vte') and terminal.vte:
            terminal.vte.feed_child((command + '\n').encode())

    def show_manager(self, widget, terminal):
        """Show snippets management window"""
        dialog = SnippetsManagerDialog(self, terminal)
        dialog.run()
        dialog.destroy()


class SnippetsManagerDialog(Gtk.Dialog):
    def __init__(self, plugin, terminal):
        Gtk.Dialog.__init__(
            self,
            title='Snippets Manager',
            parent=terminal.get_toplevel(),
            modal=True,
            destroy_with_parent=True,
            buttons=(
                Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE
            )
        )

        self.plugin = plugin
        self.set_default_size(800, 600)

        # Main layout
        vbox = Gtk.VBox(spacing=5)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)
        vbox.set_margin_top(10)
        vbox.set_margin_bottom(10)
        vbox.set_vexpand(True)
        vbox.set_hexpand(True)

        # Title
        title = Gtk.Label(label='<b>Snippets Management</b>')
        title.set_use_markup(True)
        vbox.pack_start(title, False, False, 5)

        # Scrolled area with snippets list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        scrolled.set_size_request(750, 450)

        self.tree = Gtk.TreeStore(str, str, str)  # name, command, category
        self.load_tree()

        view = Gtk.TreeView(model=self.tree)
        view.set_headers_visible(True)
        view.set_vexpand(True)
        view.set_hexpand(True)

        col1 = Gtk.TreeViewColumn('Category', Gtk.CellRendererText(), text=2)
        col1.set_expand(True)
        col2 = Gtk.TreeViewColumn('Name', Gtk.CellRendererText(), text=0)
        col2.set_expand(True)
        col3 = Gtk.TreeViewColumn('Command', Gtk.CellRendererText(), text=1)
        col3.set_expand(True)

        view.append_column(col1)
        view.append_column(col2)
        view.append_column(col3)

        scrolled.add(view)
        vbox.pack_start(scrolled, True, True, 10)

        # Action buttons
        button_box = Gtk.HBox(spacing=5)

        add_btn = Gtk.Button(label='Add')
        add_btn.connect('clicked', self.add_snippet)
        button_box.pack_start(add_btn, False, False, 0)

        edit_btn = Gtk.Button(label='Edit')
        edit_btn.connect('clicked', self.edit_snippet, view)
        button_box.pack_start(edit_btn, False, False, 0)

        delete_btn = Gtk.Button(label='Delete')
        delete_btn.connect('clicked', self.delete_snippet, view)
        button_box.pack_start(delete_btn, False, False, 0)

        vbox.pack_end(button_box, False, False, 5)

        content_area = self.get_content_area()
        content_area.add(vbox)
        content_area.set_vexpand(True)
        content_area.set_hexpand(True)
        self.show_all()

    def load_tree(self):
        """Load snippets in the tree"""
        self.tree.clear()
        for category, snippets in self.plugin.snippets.items():
            if isinstance(snippets, dict):
                category_iter = self.tree.append(None, [category, '', category])
                for name, command in snippets.items():
                    self.tree.append(category_iter, [name, command, category])

    def add_snippet(self, widget):
        """Open dialog to add new snippet"""
        dialog = Gtk.Dialog(
            title='New Snippet',
            modal=True,
            destroy_with_parent=True,
            buttons=(Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        )
        dialog.set_default_size(500, 350)

        vbox = Gtk.VBox(spacing=5)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)
        vbox.set_margin_top(10)
        vbox.set_margin_bottom(10)

        # Category
        category_label = Gtk.Label(label='Category:')
        category_label.set_xalign(0)
        category_entry = Gtk.Entry()
        category_entry.set_text('General')
        vbox.pack_start(category_label, False, False, 0)
        vbox.pack_start(category_entry, False, False, 0)

        # Name
        name_label = Gtk.Label(label='Name:')
        name_label.set_xalign(0)
        name_entry = Gtk.Entry()
        vbox.pack_start(name_label, False, False, 0)
        vbox.pack_start(name_entry, False, False, 0)

        # Command
        command_label = Gtk.Label(label='Command:')
        command_label.set_xalign(0)
        vbox.pack_start(command_label, False, False, 0)

        command_scrolled = Gtk.ScrolledWindow()
        command_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        command_scrolled.set_vexpand(True)
        command_scrolled.set_hexpand(True)
        command_text = Gtk.TextView()
        command_text.set_wrap_mode(Gtk.WrapMode.NONE)
        command_text.set_vexpand(True)
        command_text.set_hexpand(True)
        command_scrolled.add(command_text)
        vbox.pack_start(command_scrolled, True, True, 0)

        dialog.get_content_area().add(vbox)
        dialog.show_all()

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            category = category_entry.get_text() or 'General'
            name = name_entry.get_text()
            command = command_text.get_buffer().get_text(
                command_text.get_buffer().get_start_iter(),
                command_text.get_buffer().get_end_iter(),
                False
            ).strip()

            if name and command:
                if category not in self.plugin.snippets:
                    self.plugin.snippets[category] = {}

                self.plugin.snippets[category][name] = command
                self.save_snippets()
                self.load_tree()

        dialog.destroy()

    def edit_snippet(self, widget, view):
        """Open dialog to edit selected snippet"""
        selection = view.get_selection()
        model, treeiter = selection.get_selected()

        if not treeiter:
            return

        category = model.get_value(treeiter, 2)
        name = model.get_value(treeiter, 0)

        # Verify it's not a category
        if not category or name == category or name not in self.plugin.snippets.get(category, {}):
            return

        command = model.get_value(treeiter, 1)

        dialog = Gtk.Dialog(
            title='Edit Snippet',
            modal=True,
            destroy_with_parent=True,
            buttons=(Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        )
        dialog.set_default_size(500, 350)

        vbox = Gtk.VBox(spacing=5)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)
        vbox.set_margin_top(10)
        vbox.set_margin_bottom(10)

        # Category
        category_label = Gtk.Label(label='Category:')
        category_label.set_xalign(0)
        category_entry = Gtk.Entry()
        category_entry.set_text(category)
        vbox.pack_start(category_label, False, False, 0)
        vbox.pack_start(category_entry, False, False, 0)

        # Name
        name_label = Gtk.Label(label='Name:')
        name_label.set_xalign(0)
        name_entry = Gtk.Entry()
        name_entry.set_text(name)
        vbox.pack_start(name_label, False, False, 0)
        vbox.pack_start(name_entry, False, False, 0)

        # Command
        command_label = Gtk.Label(label='Command:')
        command_label.set_xalign(0)
        vbox.pack_start(command_label, False, False, 0)

        command_scrolled = Gtk.ScrolledWindow()
        command_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        command_scrolled.set_vexpand(True)
        command_scrolled.set_hexpand(True)
        command_text = Gtk.TextView()
        command_text.set_wrap_mode(Gtk.WrapMode.NONE)
        command_text.set_vexpand(True)
        command_text.set_hexpand(True)
        command_text.get_buffer().set_text(command)
        command_scrolled.add(command_text)
        vbox.pack_start(command_scrolled, True, True, 0)

        dialog.get_content_area().add(vbox)
        dialog.show_all()

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            new_category = category_entry.get_text() or category
            new_name = name_entry.get_text()
            new_command = command_text.get_buffer().get_text(
                command_text.get_buffer().get_start_iter(),
                command_text.get_buffer().get_end_iter(),
                False
            ).strip()

            if new_name and new_command:
                # Delete old entry
                del self.plugin.snippets[category][name]

                # Add new entry with potentially new category/name
                if new_category not in self.plugin.snippets:
                    self.plugin.snippets[new_category] = {}

                self.plugin.snippets[new_category][new_name] = new_command

                # Delete old category if empty
                if not self.plugin.snippets[category]:
                    del self.plugin.snippets[category]

                self.save_snippets()
                self.load_tree()

        dialog.destroy()

    def delete_snippet(self, widget, view):
        """Delete selected snippet"""
        selection = view.get_selection()
        model, treeiter = selection.get_selected()

        if treeiter:
            category = model.get_value(treeiter, 2)
            name = model.get_value(treeiter, 0)

            # Verify it's not a category
            if category and name != category and name in self.plugin.snippets.get(category, {}):
                del self.plugin.snippets[category][name]

                # Delete category if empty
                if not self.plugin.snippets[category]:
                    del self.plugin.snippets[category]

                self.save_snippets()
                self.load_tree()

    def save_snippets(self):
        """Save snippets to configuration file"""
        config_path = os.path.expanduser('~/.config/terminator/snippets.json')
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.plugin.snippets, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving snippets: {e}")
