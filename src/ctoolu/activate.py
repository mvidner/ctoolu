"""ctoolu-activate: trigger ctoolu via Unix socket."""

import json
import socket
import sys

from . import xdg


SOCKET_PATH = xdg.XDG_RUNTIME_DIR / 'ctoolu.sock'


def send_command(msg):
    """Send a JSON command to the ctoolu socket."""
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.connect(str(SOCKET_PATH))
        sock.sendall(json.dumps(msg).encode('utf-8'))
    finally:
        sock.close()


def main():
    """Entry point for ctoolu-activate.

    Usage:
        ctoolu-activate           # activate with current clipboard
        ctoolu-activate TEXT      # look at specific text
    """
    if len(sys.argv) > 1:
        text = sys.argv[1]
        send_command({'command': 'look', 'text': text})
    else:
        send_command({'command': 'activate'})


if __name__ == '__main__':
    main()
