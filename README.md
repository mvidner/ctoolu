# Ctoolu

Ctoolu (Clipboard Tool, Universal, pronounced "cthulhu") matches
patterns in the clipboard text and pops up menus to execute actions.
It is inspired by http://en.wikipedia.org/wiki/Klipper but aims to be
more modular in its configuration.

## Usage

Ensure ctoolu is launched either manually or via `ctoolu.desktop` by
restarting your desktop session.

When text which matches one of the patterns is copied to the clipboard, you
will see a popup menu. You can also sidestep the clipboard via
`ctoolu-activate "TEXT"`

## Examples of patterns:

- bnc#778347   https://bugzilla.novell.com/show_bug.cgi?id=778347
- kde#273792   https://bugs.kde.org/show_bug.cgi?id=273792
- bgo#597386   https://bugzilla.gnome.org/show_bug.cgi?id=597386
- fdo#34070    https://bugs.freedesktop.org/show_bug.cgi?id=34070
- LP: #920197  https://bugs.launchpad.net/bugs/920197
- fate#100011  https://features.opensuse.org/100011

## Get it

https://github.com/mvidner/ctoolu

## Requirements

- ruby-gtk2
- ruby-dbus gem

### Getting the requirements on openSUSE

    V=`sed -n '/VERSION *= */s///;T;p' /etc/SuSE-release`
    sudo zypper ar http://download.opensuse.org/repositories/home:/Lazy_Kent/openSUSE_$V lazykent
    sudo zypper in rubygems rubygem-rake rubygem-ruby-dbus ruby-gtk2

## Installation

Install system-wide via:

    sudo rake install

or for the current user via:

    rake install_user

It will install `clipboard-relay` on the session D-Bus and set up ctoolu for
session autostart.

## Configuration

Edit `ctoolu.yaml` in `/etc/xdg` (for system-wide installations) or
`$HOME/.config` (for per-user installations) to have it watch the
primary selection instead of the clipboard, or to switch from
automatic to explicit activation via `ctoolu-activate`.

The patterns to be matched, and actions offered via the pop-up menu
are defined in YAML files under `/usr/share/ctoolu` (for system-wide
installations) or `$HOME/.local/share/ctoolu` (for per-user
installations).  See the existing files for example syntax.

## Support / known issues

Please visit https://github.com/mvidner/ctoolu/issues to see known
issues and report new issues or feature requests.

## License

[GPL-2.0](http://www.spdx.org/licenses/GPL-2.0)
