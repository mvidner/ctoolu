"""XDG Base Directory Specification helpers."""

import os
from pathlib import Path


HOME = Path.home()

XDG_DATA_HOME = Path(os.environ.get('XDG_DATA_HOME', HOME / '.local' / 'share'))
XDG_DATA_DIRS = [XDG_DATA_HOME] + [
    Path(d) for d in
    os.environ.get('XDG_DATA_DIRS', '/usr/local/share:/usr/share').split(':')
]

XDG_CONFIG_HOME = Path(os.environ.get('XDG_CONFIG_HOME', HOME / '.config'))
XDG_CONFIG_DIRS = [XDG_CONFIG_HOME] + [
    Path(d) for d in
    os.environ.get('XDG_CONFIG_DIRS', '/etc/xdg').split(':')
]

XDG_RUNTIME_DIR = Path(os.environ.get('XDG_RUNTIME_DIR', f'/run/user/{os.getuid()}'))


def load_data_paths(resource):
    """Return list of existing absolute paths for a data resource."""
    paths = [d / resource for d in XDG_DATA_DIRS]
    return [p for p in paths if p.is_absolute() and p.exists()]


def load_config_paths(resource):
    """Return list of existing absolute paths for a config resource."""
    paths = [d / resource for d in XDG_CONFIG_DIRS]
    return [p for p in paths if p.is_absolute() and p.exists()]


def load_first_config(resource):
    """Return the first existing config path for a resource, or None."""
    paths = load_config_paths(resource)
    return paths[0] if paths else None
