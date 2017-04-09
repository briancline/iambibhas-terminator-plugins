"""A Terminator plugin to post the selected text in a terminal to Hastebin.
If successful, the default browser is opened with your hastebin link.

A custom Hastebin URL can optionally be provided in your Terminator
configuration by setting the `base_url` option, which is useful if you use a
custom one on your own domain, or internally at work, etc. Defaults to
https://hastebin.com.

    [plugins]
      [[HastebinPlugin]]
        base_url = https://hastebin.mydomain.local


Written by Bibhas Debnath (http://bibhas.in).
Improvements by Brian Cline (https://github.com/briancline).
"""
import gtk
import requests
from terminatorlib import config
from terminatorlib import plugin
from terminatorlib.translation import _
from terminatorlib import util


AVAILABLE = ['HastebinPlugin']  # Plugin classes to expose to Terminator


class HastebinPlugin(plugin.Plugin):
    capabilities = ['terminal_menu']

    def __init__(self):
        cfg = config.Config()
        self.base_url = cfg.plugin_get(
            self.__class__.__name__, 'base_url',
            'https://hastebin.com').rstrip('/')

    def do_upload(self, widget, terminal):
        """Upload to Hastebin and opens a browser with the link."""
        text = gtk.clipboard_get(gtk.gdk.SELECTION_PRIMARY).wait_for_text()
        resp = requests.post(self.base_url + '/documents', data=text)

        if resp.status_code not in (200, 201, 202):
            util.err(_('Hastebin error: HTTP %d: %s') %
                     (resp.status_code, resp.text))
            return

        gtk.show_uri(None, self.base_url + '/' + resp.json()['key'],
                     gtk.gdk.CURRENT_TIME)

    def callback(self, menuitems, menu, terminal):
        """Add Hastebin item to a terminal's context menu."""
        item = gtk.ImageMenuItem(gtk.STOCK_PASTE)
        item.connect('activate', self.do_upload, terminal)
        item.set_label(_('Upload to Hastebin'))
        item.set_sensitive(terminal.vte.get_has_selection())
        item.set_use_underline(False)
        menuitems.append(item)
