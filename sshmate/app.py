import os

import pyfiglet
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Footer, Input, Label, ListItem, ListView, Static

from . import storage

BANNER = pyfiglet.figlet_format("sshmate", font="slant")


class ConfirmDelete(ModalScreen):
    CSS = """
    ConfirmDelete {
        align: center middle;
    }
    #confirm-container {
        background: $surface;
        border: solid $error;
        padding: 2 4;
        width: 48;
        height: auto;
    }
    #confirm-title {
        text-align: center;
        color: $error;
        text-style: bold;
        margin-bottom: 1;
    }
    #confirm-message {
        text-align: center;
        margin-bottom: 2;
    }
    #buttons {
        align: center middle;
        height: auto;
    }
    Button {
        margin: 0 1;
    }
    """

    def __init__(self, alias: str):
        super().__init__()
        self.alias = alias

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-container"):
            yield Static("Delete Connection", id="confirm-title")
            yield Static(f'Delete "{self.alias}"?', id="confirm-message")
            with Horizontal(id="buttons"):
                yield Button("Delete", variant="error", id="confirm")
                yield Button("Cancel", variant="default", id="cancel")

    def on_button_pressed(self, event: Button.Pressed):
        self.dismiss(event.button.id == "confirm")


class ConnectionForm(Screen):
    CSS = """
    ConnectionForm {
        align: center middle;
    }
    #form-container {
        background: $surface;
        border: solid $primary;
        padding: 2 4;
        width: 64;
        height: auto;
    }
    #form-title {
        text-align: center;
        color: $primary;
        text-style: bold;
        margin-bottom: 1;
    }
    Label {
        margin-top: 1;
        color: $text-muted;
    }
    Input {
        margin-top: 0;
    }
    #buttons {
        margin-top: 2;
        height: auto;
    }
    Button {
        margin-right: 1;
    }
    """

    def __init__(self, connection=None):
        super().__init__()
        self.connection = connection or {}

    def compose(self) -> ComposeResult:
        title = "Edit Connection" if self.connection else "Add Connection"
        with Vertical(id="form-container"):
            yield Static(title, id="form-title")
            yield Label("Alias")
            yield Input(value=self.connection.get("alias", ""), id="alias", placeholder="e.g. prod-server")
            yield Label("User")
            yield Input(value=self.connection.get("user", ""), id="user", placeholder="e.g. ubuntu")
            yield Label("Host")
            yield Input(value=self.connection.get("host", ""), id="host", placeholder="e.g. 192.168.1.1")
            yield Label("Port")
            yield Input(value=self.connection.get("port", "22"), id="port", placeholder="22")
            yield Label("Key path (optional)")
            yield Input(value=self.connection.get("key", ""), id="key", placeholder="~/.ssh/id_rsa")
            with Horizontal(id="buttons"):
                yield Button("Save", variant="primary", id="save")
                yield Button("Cancel", variant="default", id="cancel")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "save":
            alias = self.query_one("#alias", Input).value.strip()
            user = self.query_one("#user", Input).value.strip()
            host = self.query_one("#host", Input).value.strip()
            port = self.query_one("#port", Input).value.strip() or "22"
            key = self.query_one("#key", Input).value.strip()
            if not alias or not host:
                return
            self.dismiss({"alias": alias, "user": user, "host": host, "port": port, "key": key})


class SSHMateApp(App):
    BINDINGS = [
        Binding("e", "edit", "Edit"),
        Binding("d", "delete", "Delete"),
        Binding("q", "quit", "Quit"),
    ]

    CSS = """
    Screen {
        background: $background;
    }
    #banner {
        text-align: center;
        color: $success;
        padding: 1 0 0 0;
    }
    #subtitle {
        text-align: center;
        color: $text-muted;
        margin-bottom: 1;
    }
    ListView {
        border: solid $primary;
        margin: 0 4;
        height: auto;
        max-height: 20;
    }
    ListItem {
        padding: 0 1;
    }
    """

    def __init__(self):
        super().__init__()
        self.connections = storage.load()

    def compose(self) -> ComposeResult:
        yield Static(BANNER, id="banner")
        yield Static("SSH Connection Manager", id="subtitle")
        yield ListView(id="connection-list")
        yield Footer()

    def on_mount(self):
        self._refresh_list()

    def _refresh_list(self):
        lv = self.query_one("#connection-list", ListView)
        lv.clear()
        for conn in self.connections:
            user = conn.get("user", "")
            host = conn["host"]
            port = conn.get("port", "22")
            detail = f"{user}@{host}" if user else host
            if port != "22":
                detail += f":{port}"
            lv.append(ListItem(Label(f"{conn['alias']}  [{detail}]")))
        lv.append(ListItem(Label("+ Add new")))

    def on_list_view_selected(self, event: ListView.Selected):
        index = event.list_view.index
        if index is None:
            return
        if index >= len(self.connections):
            self._add_connection()
        else:
            self.exit(self.connections[index])

    def action_edit(self):
        lv = self.query_one("#connection-list", ListView)
        index = lv.index
        if index is None or index >= len(self.connections):
            return

        def on_result(result):
            if result:
                self.connections[index] = result
                storage.save(self.connections)
                self._refresh_list()

        self.push_screen(ConnectionForm(self.connections[index]), on_result)

    def action_delete(self):
        lv = self.query_one("#connection-list", ListView)
        index = lv.index
        if index is None or index >= len(self.connections):
            return
        alias = self.connections[index]["alias"]

        def on_result(confirmed):
            if confirmed:
                self.connections.pop(index)
                storage.save(self.connections)
                self._refresh_list()

        self.push_screen(ConfirmDelete(alias), on_result)

    def _add_connection(self):
        def on_result(result):
            if result:
                self.connections.append(result)
                storage.save(self.connections)
                self._refresh_list()

        self.push_screen(ConnectionForm(), on_result)


def main():
    app = SSHMateApp()
    connection = app.run()
    if connection:
        cmd = ["ssh"]
        key = connection.get("key", "")
        if key:
            cmd += ["-i", os.path.expanduser(key)]
        port = connection.get("port", "22")
        if port and port != "22":
            cmd += ["-p", port]
        user = connection.get("user", "")
        host = connection["host"]
        cmd.append(f"{user}@{host}" if user else host)
        os.execvp("ssh", cmd)
