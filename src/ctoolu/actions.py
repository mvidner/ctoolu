"""Loading and matching of clipboard actions."""

import re
from dataclasses import dataclass, field
from pathlib import Path
import yaml
import os
import logging

from . import xdg


# POSIX character class to Python regex equivalent
POSIX_CLASSES = {
    '[:alnum:]': 'a-zA-Z0-9',
    '[:alpha:]': 'a-zA-Z',
    '[:blank:]': ' \\t',
    '[:cntrl:]': '\\x00-\\x1f\\x7f',
    '[:digit:]': '0-9',
    '[:graph:]': '!-~',
    '[:lower:]': 'a-z',
    '[:print:]': ' -~',
    '[:punct:]': '!-/:-@\\[-`{-~',
    '[:space:]': ' \\t\\n\\r\\f\\v',
    '[:upper:]': 'A-Z',
    '[:xdigit:]': '0-9a-fA-F',
}


def posix_ere_to_python(pattern):
    """Convert a POSIX Extended Regular Expression to a Python regex string.

    Translates POSIX character classes like [[:digit:]] to Python equivalents.

    >>> posix_ere_to_python('[[:digit:]]+')
    '[0-9]+'
    >>> posix_ere_to_python('[[:alpha:]][^[:space:]]+')
    '[a-zA-Z][^\\\\s]+'
    >>> posix_ere_to_python('[[:digit:][:alpha:]]+')
    '[0-9a-zA-Z]+'
    """
    result = pattern
    for posix_class, python_equiv in POSIX_CLASSES.items():
        result = result.replace(posix_class, python_equiv)
    return result


def substitute(template, captures):
    """Substitute captures into a template string.

    Supports both %s (sequential) and %N$s (positional, 1-indexed) formats.

    >>> substitute('https://example.com/%s', ['123'])
    'https://example.com/123'
    >>> substitute('id=%1$s&id=%1$s', ['42'])
    'id=42&id=42'
    >>> substitute('%s/%s', ['foo', 'bar'])
    'foo/bar'
    """
    # First, handle %N$s positional references
    def replace_positional(m):
        idx = int(m.group(1)) - 1
        return captures[idx]
    result = re.sub(r'%(\d+)\$s', replace_positional, template)

    # Then, handle %s sequential references
    capture_iter = iter(captures)

    def replace_sequential(m):
        return next(capture_iter)
    result = re.sub(r'%s', replace_sequential, result)
    return result


@dataclass
class CtooluCommand:
    label: str
    command: str
    keep_output: bool = False

    def execute(self, captures, set_clipboard):
        """Execute the command with substituted captures.

        Args:
            captures: List of regex capture group strings.
            set_clipboard: Callable to set clipboard text.
        """
        import subprocess

        substituted = substitute(self.command, captures)
        if self.keep_output:
            result = subprocess.run(
                substituted, shell=True, capture_output=True, text=True,
            )
            set_clipboard(result.stdout.rstrip('\n'))
        else:
            subprocess.Popen(
                substituted, shell=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )


@dataclass
class CtooluAction:
    label: str
    regex: re.Pattern
    url: str = None
    commands: list = field(default_factory=list)

    def match(self, text):
        """Return the match object if the text matches, else None."""
        return self.regex.search(text)


def _parse_action(data):
    """Parse a single action dict from YAML into a CtooluAction."""
    pattern_str = data.get('regex', '')
    case_sensitive = data.get('case_sensitive', True)

    python_pattern = posix_ere_to_python(pattern_str)
    flags = 0 if case_sensitive else re.IGNORECASE
    compiled = re.compile(python_pattern, flags)

    commands = []
    for cmd_data in data.get('commands', []):
        commands.append(CtooluCommand(
            label=cmd_data['label'],
            command=cmd_data['command'],
            keep_output=cmd_data.get('keep_output', False),
        ))

    return CtooluAction(
        label=data['label'],
        regex=compiled,
        url=data.get('url'),
        commands=commands,
    )


def load_actions():
    """Load all actions from XDG and code-adjacent data directories

    Files in higher-priority directories (user) override lower-priority
    (system) ones with the same basename.
    """
    seen_basenames = set()
    actions = []

    here_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../data/ctoolu')
    data_dirs = xdg.load_data_paths('ctoolu') + [here_dir]
    logging.info(f"Data dirs: {data_dirs}")
    for data_dir in data_dirs:
        for yaml_file in sorted(Path(data_dir).glob('*.yaml')):
            basename = yaml_file.name
            if basename in seen_basenames:
                continue

            seen_basenames.add(basename)
            with open(yaml_file) as f:
                file_actions = yaml.safe_load(f)
            if file_actions:
                for action_data in file_actions:
                    actions.append(_parse_action(action_data))

    if not actions:
        raise RuntimeError(
            'No rules found. Check XDG_DATA_HOME/ctoolu/ and XDG_DATA_DIRS'
        )
    return actions


def match_actions(text, actions):
    """Return list of (action, match) tuples for text.

    >>> action = CtooluAction('Test', re.compile(r'bug#(\\d+)', re.I), 'http://example.com/%s')
    >>> matches = match_actions('bug#123', [action])
    >>> len(matches)
    1
    >>> matches[0][1].group(1)
    '123'
    """
    results = []
    for action in actions:
        m = action.match(text)
        if m:
            results.append((action, m))
    return results
