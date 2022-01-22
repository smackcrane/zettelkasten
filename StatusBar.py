############################################################################
# 
#   StatusBar.py
#       curses window (container) for status bar
#   
############################################################################

import curses
from Keys import Keys

class StatusBar:
    def __init__(self, win):
        # curses window we're living in
        self.win = win
        # ID if relevant
        self.ID = None
        # text to display
        self.text = ''
        # search text when searching
        self.search_text = ''
        # attribute for display, default reverse for contrast
        self.attr = curses.A_REVERSE
        # flag for search in progress
        self.searching = False

        self.refresh()

    def getbegyx(self):
        return self.win.getbegyx()

    def getmaxyx(self):
        return self.win.getmaxyx()

    def refresh(self):
        self.win.erase()
        curses.curs_set(0) # hide cursor
        if self.ID:
            display = self.ID.ljust(9)+self.text
        else:
            display = self.text
        display += ' '*curses.COLS # pad with spaces to light up whole bar
        self.win.insstr( 0,0, display, self.attr )
        self.win.refresh()

    def start_search(self):
        self.searching = True
        self.search_text = ''

    def end_search(self):
        self.searching = False
        self.text = ''
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
            # don't backspace '/' when searching
            if len(self.search_text) > 0:
                self.text = self.text[:-1]
                self.search_text = self.search_text[:-1]
        elif 32 <= k <= 126: # only include "regular" characters
            self.text += chr(k)
            self.search_text += chr(k)
        self.refresh()

    def keypress(self, k):
        flag, val = None, None
        if k == Keys.ESC:
            self.end_search()
        elif self.searching:
            self.insert(k)
        else:
            self.echo(k)

        return flag, val
