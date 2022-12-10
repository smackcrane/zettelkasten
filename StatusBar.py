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
        _, self.cols = self.win.getmaxyx()
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

    def debugger(self, s='', state=False, log=None):
        if not log:
            log = '/dev/pts/4'
        with open(log, 'a') as f:
            print(s, file=f)
            if state:
                print(f'self.text: {self.text}\n'
                        + f'self.search_text: {self.search_text}\n'
                        + f'self.command_text: {self.command_text}\n'
                        + f'self.searching: {self.searching}\n'
                        + f'self.command_mode: {self.command_mode}\n',
                file=f)

    def refresh(self, text=None):
        if text == None:    # default
            text = self.text
        self.win.erase()
        curses.curs_set(0) # hide cursor
        # pad with spaces to light up whole bar
        display = text + ' '*self.cols
        self.win.insstr( 0,0, display, self.attr )
        self.win.refresh()

    def preview_ID(self, ID):
        if ID: # may be None
            title = utils.get_title(ID)
            text = ID.ljust(9) + title
            self.refresh(text)

    def set(self, text):
        self.text = text
        self.refresh()

    def start_search(self):
        self.searching = True
        self.text = '/'
        self.search_text = ''
        self.refresh()

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
        instruction = None  # instructions to pass back to zk.py
        if 'protograph' in self.command_text:
            if 'directed' in self.command_text:
                directed = True
                self.text = 'protographing (directed) ...'
            else:
                directed = False
                self.text = 'protographing ...'
            self.refresh()
            try:
                utils.protograph(directed)
                self.text = ''
            except Exception as e:
                self.text = 'ERROR: ' + str(e)
        elif self.command_text == 'count':
            instruction = 'count'
        elif self.command_text == 'sort':
            instruction = 'sort'
        else:
            self.text = f'command "{self.command_text}" not recognized'
        self.refresh()
        return instruction

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

    def resize(self, screen_rows, screen_cols):
        self.cols = screen_cols
        self.win = curses.newwin( 1,screen_cols, screen_rows-1,0 )
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
        text = 'ERROR: ' + str(e)
        self.refresh(text)
