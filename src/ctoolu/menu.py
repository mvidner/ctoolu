"""Qt popup menu for matched actions."""

from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtGui import QCursor

from .actions import substitute


def _add_mnemonic(label, used):
    """Add a Qt mnemonic (``&`` prefix) to an unused letter in *label*.

    Prefers word-initial letters, then falls back to any letter.
    Modifies *used* in place by adding the chosen letter (lowercased).
    Returns the label unchanged if no unique letter is available.

    >>> used = set()
    >>> _add_mnemonic('Open browser', used)
    '&Open browser'
    >>> _add_mnemonic('Open folder', used)
    'Open &folder'
    >>> _add_mnemonic('Copy text', used)
    'Copy &text'
    """
    # First pass: try word-initial letters
    for i, ch in enumerate(label):
        if ch.isalpha() and (i == 0 or not label[i - 1].isalpha()) \
                and ch.lower() not in used:
            used.add(ch.lower())
            return label[:i] + '&' + label[i:]
    # Second pass: any letter
    for i, ch in enumerate(label):
        if ch.isalpha() and ch.lower() not in used:
            used.add(ch.lower())
            return label[:i] + '&' + label[i:]
    return label


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
    used_mnemonics = set()

    for action, match in matches:
        if not first_group:
            menu.addSeparator()
        first_group = False

        captures = list(match.groups())
        match_text = match.group(0)

        # Group header: clicking it sets the clipboard to the URL
        header_label = _add_mnemonic(
            f'{action.label} ({match_text})', used_mnemonics,
        )
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
            cmd_label = _add_mnemonic(f'  {cmd.label}', used_mnemonics)
            cmd_action = menu.addAction(cmd_label)
            cmd_action.triggered.connect(
                lambda checked, c=cmd, caps=captures: c.execute(caps, set_clipboard)
            )

    menu.addSeparator()
    menu.addAction('Cancel')

    menu.popup(QCursor.pos())
    # Keep a reference so the menu isn't garbage collected
    menu._prevent_gc = menu
    menu.aboutToHide.connect(lambda: menu.deleteLater())
