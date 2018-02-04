import pygtk
pygtk.require('2.0')
import gtk
import wnck
import re
import sys
import time

screen = wnck.screen_get_default()
while gtk.events_pending():
    gtk.main_iteration()

titlePattern = re.compile('Hoaul')

windows = screen.get_windows()
for w in windows:
  if titlePattern.match(w.get_name()):
    print w.get_name()
    w.activate(int(time.time()))
