"""Qt popup menu for matched actions."""

from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtGui import QCursor

from .actions import substitute


def show_menu(matches, set_clipboard):
    """Show a popup menu for the matched actions.

    Args:
        matches: List of (CtooluAction, re.Match) tuples.
        set_clipboard: Callable to set clipboard text.
    """
    if not matches:
        return

    menu = QMenu()
    first_group = True

    for action, match in matches:
        if not first_group:
            menu.addSeparator()
        first_group = False

        captures = list(match.groups())
        match_text = match.group(0)

        # Group header: clicking it sets the clipboard to the URL
        header_label = f'{action.label} ({match_text})'
        if action.url:
            url = substitute(action.url, captures)
            header_action = menu.addAction(header_label)
            header_action.triggered.connect(
                lambda checked, u=url: set_clipboard(u)
            )
        else:
            header_action = menu.addAction(header_label)
            header_action.setEnabled(False)

        # Command items
        for cmd in action.commands:
            cmd_action = menu.addAction(f'  {cmd.label}')
            cmd_action.triggered.connect(
                lambda checked, c=cmd, caps=captures: c.execute(caps, set_clipboard)
            )

    menu.addSeparator()
    menu.addAction('Cancel')

    menu.popup(QCursor.pos())
    # Keep a reference so the menu isn't garbage collected
    menu._prevent_gc = menu
    menu.aboutToHide.connect(lambda: menu.deleteLater())
