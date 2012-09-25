# Ctoolu

Ctoolu (Clipboard Tool, Universal, pronounced "cthulhu") matches
patterns in the clipboard text and pops up menus to execute actions.
It is inspired by http://en.wikipedia.org/wiki/Klipper but aims to be
more modular in its configuration.

## Examples of patterns:

- bnc#778347   https://bugzilla.novell.com/show_bug.cgi?id=778347
- kde#273792   https://bugs.kde.org/show_bug.cgi?id=273792
- bgo#597386   https://bugzilla.gnome.org/show_bug.cgi?id=597386
- fdo#34070    https://bugs.freedesktop.org/show_bug.cgi?id=34070
- lp#920197    https://bugs.launchpad.net/bugs/920197
- fate#100011  https://features.opensuse.org/100011

## Get it

https://github.com/mvidner/ctoolu

## Installation

    sudo rake install

or
    rake install_user

It will install clipboard-relay on the session D-Bus and set up ctoolu for
session autostart.

*FIXME* it will overwrite the configuration file if it is already installed.

## Usage

Ensure ctoolu is launched either manually or via ctoolu.desktop by
restarting your desktop session.  When text which matches one of the
pattern is copied to the clipboard, you will see a popup menu.

## Requirements

- ruby-gtk2
- ruby-dbus

### Getting the requirements on openSUSE

    V=`sed -n '/VERSION *= */s///;T;p' /etc/SuSE-release`
    sudo zypper ar http://download.opensuse.org/repositories/home:/Lazy_Kent/openSUSE_$V lazykent
    sudo zypper in rubygems rubygem-rake rubygem-ruby-dbus ruby-gtk2

## License

GPLv2
