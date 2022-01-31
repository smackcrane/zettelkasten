############################################################################
# 
#   StatusBar.py
#       curses window (container) for status bar
#   
############################################################################

import curses
import utils
from Keys import Keys

class StatusBar:
    def __init__(self, win):
        # curses window we're living in
        self.win = win
        # text to display
        self.text = ''
        # search text when searching
        self.search_text = ''
        # command text when commanding
        self.command_text = ''
        # attribute for display, default reverse for contrast
        self.attr = curses.A_REVERSE
        # flag for search in progress
        self.searching = False
        # flag for command in progress
        self.command_mode = False

        self.refresh()

    def refresh(self):
        self.win.erase()
        curses.curs_set(0) # hide cursor
        # pad with spaces to light up whole bar
        display = self.text + ' '*curses.COLS
        self.win.insstr( 0,0, display, self.attr )
        self.win.refresh()

    def set(self, text):
        self.text = text
        self.refresh()

    def start_search(self):
        self.searching = True
        self.search_text = ''

    def end_search(self):
        self.searching = False
        self.text = ''
        self.refresh()

    def start_command(self):
        self.command_mode = True
        self.command_text = ''

    def end_command(self):
        self.command_mode = False
        self.text = ''
        self.refresh()

    def exec_command(self):
        self.command_mode = False
        self.text = ''
        if self.command_text == 'protograph':
            self.text = 'protographing ...'
            self.refresh()
            try:
                utils.protograph()
                self.text = ''
            except Exception as e:
                self.text = 'ERROR: ' + str(e)
        else:
            self.text = f'command "{self.command_text}" not recognized'
        self.refresh()


    def echo(self, k):
        s = ''
        # search known keys to see if we have a name for it
        known_keys = Keys.__dict__
        for key in known_keys.keys():
            if known_keys[key] == k:
                s = key
        # if no name found, just echo the character
        if not s:
            s = chr(k)
        self.text = s
        self.refresh()

    def insert(self, k):
        if k == Keys.BACKSPACE:
            # don't backspace '/' when searching or ':' in command mode
            if self.searching and len(self.search_text) > 0:
                self.text = self.text[:-1]
                self.search_text = self.search_text[:-1]
            elif self.command_mode and len(self.command_text) > 0:
                self.text = self.text[:-1]
                self.command_text = self.command_text[:-1]
        elif 32 <= k <= 126: # only include "regular" characters
            self.text += chr(k)
            self.search_text += chr(k)
            self.command_text += chr(k)
        self.refresh()

    def keypress(self, k):
        flag, val = None, None
        if k == Keys.ESC:
            if self.searching:
                self.end_search()
            elif self.command_mode:
                self.end_command()
            else:
                self.echo(k)
        elif self.searching or self.command_mode:
            self.insert(k)
        else:
            self.echo(k)

        return flag, val

    def error(self, e):
        self.text = 'ERROR: ' + str(e)
        self.refresh()
