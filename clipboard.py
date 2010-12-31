#! /usr/bin/env python
# relays Clipboard and Primary changes over DBus
import pygtk
pygtk.require('2.0')
import gtk
import dbus
import dbus.service

# must be set before we ask for signals
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

import gobject
loop = gobject.MainLoop()

class ClipboardRelay(dbus.service.Object):
	def __init__(self, path, gtk_id):
		dbus.service.Object.__init__(self, dbus.SessionBus(), path)
		self.gtk_clipboard = gtk.clipboard_get(gtk_id)
		self.gtk_clipboard.connect("owner-change", self.owner_change)
		self.gtk_clipboard.request_text(self.callback)

	def owner_change(self, gtk_clipboard, event, data=None):
		# print "OC c: %r e: %r d: %r" % (gtk_clipboard, event, data)
		gtk_clipboard.request_text(self.callback)

	def callback(self, gtk_clipboard, text, data):
		# print "CB c: %r t: %r d: %r" % (clipboard, text, data)
		self.Changed(text)

	@dbus.service.signal(dbus_interface='net.vidner.ClipboardRelay',
			     signature='s')
	def Changed(self, value):
		print "*** %s" % value
		pass

#gtk.main()
clipboard = ClipboardRelay("/net/vidner/ClipboardRelay/Clipboard",
			   gtk.gdk.SELECTION_CLIPBOARD)
primary   = ClipboardRelay("/net/vidner/ClipboardRelay/Primary",
			   gtk.gdk.SELECTION_PRIMARY)
loop.run()
