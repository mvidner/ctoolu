"""Main entry point for ctoolu."""

import json
import os
import signal
import socket
import sys

import yaml

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSocketNotifier, QTimer, pyqtSignal, QObject

from . import xdg
from .actions import load_actions, match_actions
from .menu import show_menu


SOCKET_PATH = xdg.XDG_RUNTIME_DIR / 'ctoolu.sock'


class Ctoolu(QObject):
    # Signal to handle socket requests on the main thread (Qt requirement)
    _look_signal = pyqtSignal(str)

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.clipboard = app.clipboard()
        self.actions = load_actions()
        self.config = self._load_config()
        self._look_signal.connect(self._on_look)

        if self.config.get('auto_activate', True):
            self.clipboard.dataChanged.connect(self._on_clipboard_changed)

        self._setup_socket()

    def _load_config(self):
        config_path = xdg.load_first_config('ctoolu.yaml')
        if config_path is None:
            return {}
        with open(config_path) as f:
            return yaml.safe_load(f) or {}

    def _on_clipboard_changed(self):
        text = self._get_clipboard_text()
        if text:
            self.look(text)

    def _get_clipboard_text(self):
        source = self.config.get('text_source', 'clipboard')
        if source == 'primary':
            return self.clipboard.text(self.clipboard.Selection)
        else:
            return self.clipboard.text()

    def look(self, text):
        matches = match_actions(text, self.actions)
        if matches:
            show_menu(matches, self._set_clipboard)

    def _on_look(self, text):
        """Handle look request from socket (runs on main thread)."""
        self.look(text)

    def _set_clipboard(self, text):
        self.clipboard.setText(text)

    def _setup_socket(self):
        """Set up a Unix domain socket for ctoolu-activate."""
        if SOCKET_PATH.exists():
            SOCKET_PATH.unlink()

        self._server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._server_socket.bind(str(SOCKET_PATH))
        self._server_socket.listen(5)
        self._server_socket.setblocking(False)

        self._notifier = QSocketNotifier(
            self._server_socket.fileno(),
            QSocketNotifier.Read,
        )
        self._notifier.activated.connect(self._on_socket_connection)

    def _on_socket_connection(self):
        """Accept a connection on the Unix socket."""
        try:
            conn, _ = self._server_socket.accept()
        except BlockingIOError:
            return

        with conn:
            data = conn.recv(4096).decode('utf-8', errors='replace')

        try:
            msg = json.loads(data)
        except json.JSONDecodeError:
            return

        command = msg.get('command')
        if command == 'look':
            text = msg.get('text', '')
            self._look_signal.emit(text)
        elif command == 'activate':
            text = self._get_clipboard_text()
            if text:
                self._look_signal.emit(text)

    def cleanup(self):
        self._server_socket.close()
        if SOCKET_PATH.exists():
            SOCKET_PATH.unlink()


def main():
    app = QApplication(sys.argv)
    # Don't quit when popup menu closes
    app.setQuitOnLastWindowClosed(False)

    ctoolu = Ctoolu(app)

    # Handle SIGINT/SIGTERM gracefully
    def handle_signal(signum, frame):
        ctoolu.cleanup()
        app.quit()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # QTimer with a Python callback forces the interpreter to run periodically,
    # which is needed for Python signal handlers to execute during Qt's event loop.
    signal_timer = QTimer()
    signal_timer.start(500)
    signal_timer.timeout.connect(lambda: None)

    try:
        sys.exit(app.exec_())
    finally:
        ctoolu.cleanup()


if __name__ == '__main__':
    main()
