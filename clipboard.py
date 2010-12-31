import pygtk
pygtk.require('2.0')
import gtk

listeners = { "clipboard": [], "primary": [] }

def notify_listeners(type, text):
	for listener in listeners[type]:
		listener(text)

def add_listener(type, listener):
	listeners[type].append(listener)

def callback_clipboard(clipboard, text, data):
	notify_listeners("clipboard", text)
def callback_primary(clipboard, text, data):
	notify_listeners("primary", text)

def __owner_change_clipboard(clipboard, event, data=None):
	selection["clipboard"].request_text(callback_clipboard)
def __owner_change_primary(clipboard, event, data=None):
	selection["primary"].request_text(callback_primary)

selection = {}

if True:
	selection["clipboard"] = gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD)
	selection["clipboard"].request_text(callback_clipboard)
	selection["clipboard"].connect("owner-change", __owner_change_clipboard)

if True:
	selection["primary"] = gtk.clipboard_get(gtk.gdk.SELECTION_PRIMARY)
	selection["primary"].request_text(callback_primary)
	selection["primary"].connect("owner-change", __owner_change_primary)

def printer(arg):
	print arg

add_listener("clipboard", printer)

gtk.main()
