#!/usr/bin/env ruby
require 'Qt'

app = Qt::Application.new(ARGV)
# Qt.debug_level = Qt::DebugLevel::High

menu = Qt::Menu.new

click = menu.add_action("Clickme")
click.connect(SIGNAL :triggered) do
  puts "Clicked"
end
quit = Qt::Action.new("Quitme", menu) do
  connect(SIGNAL :triggered) { app.quit }
end
f = quit.font
f.set_bold(true)                # f.set_italic(true) 
quit.font = f
menu.add_action(quit)

menu.exec
