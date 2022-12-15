############################################################################
#
#   Index.py
#       table of contents curses window (container) for zettelkasten
#
############################################################################

import traceback
import curses
import config
import utils
from Keys import Keys

class Index:
    def __init__(self, win):
        # curses window we're living in
        self.win = win
        # dimensions of window
        self.rows, self.cols = self.win.getmaxyx()
        # active 'cursor' row
        self.row = 0
        # top row in view
        self.top = 0
        # flag for search in progress
        self.searching = False
        # flag for command in progress
        self.command_mode = False
        # flag for preview mode
        self.preview = False
        
        # compile list of zettel IDs and titles
        self.zett = utils.list_IDs_titles()

        self.refresh()

    def getbegyx(self):
        return self.win.getbegyx()

    def getmaxyx(self):
        return self.win.getmaxyx()

    def debugger(self, s='', state=False, log=None):
        if not log:
            log = config.logfile
        with open(log, 'a') as f:
            print(s, file=f)
            if state:
                print(f'self.row: {self.row}\n'
                        + f'self.top: {self.top}\n'
                        + f'self.searching: {self.searching}\n'
                        + f'self.command_mode: {self.command_mode}\n'
                        + f'len(self.zett): {len(self.zett)}\n',
                file=f)

    def start_search(self):
        self.searching = True

    def end_search(self):
        self.searching = False
        return self.active_ID()

    def search(self, text):
        self.zett = utils.search_IDs_titles(text)
        self.top = 0 # make sure we see search results
        if self.row >= len(self.zett): # move cursor up if it fell off
            self.row = max(0, len(self.zett) - 1)
        self.refresh()

    def start_command(self):
        self.command_mode = True

    def end_command(self):
        self.command_mode = False

    def active_ID(self):
        if self.zett:
            return self.zett[self.row]['ID']
        else:
            return None

    def sort(self):
        self.zett.sort(key=lambda zettel: utils.ID_sort(zettel['ID']))
        self.refresh()

    def update_list(self):
        self.zett = utils.list_IDs_titles()
        self.refresh()

    def refresh(self):
        self.win.erase()
        # for each visible line
        for i in range(self.top, min(self.top+self.rows, len(self.zett))):
            # i = row in zettel list, j = row in window
            j = i - self.top
            # add ID and title, highlighting ID on active row
            if self.zett[i]['TITLE']: # allow None title without error
                self.win.insstr( j,0, self.zett[i]['TITLE'])
            if i == self.row:
                self.win.insstr( j,0, ' '*(9-len(self.zett[i]['ID'])))
                self.win.insstr( j,0, self.zett[i]['ID'], curses.A_REVERSE)
            else:
                self.win.insstr( j,0, self.zett[i]['ID'].ljust(9))
        curses.curs_set(0) # hide cursor
        self.win.refresh()

    def resize(self, screen_rows, screen_cols):
        self.rows, self.cols = screen_rows - 1, screen_cols
        self.win = curses.newwin(self.rows, self.cols)
        self.refresh()

    def keypress(self, k):
        flag, val = None, None
        if k == Keys.UP:            self.up()
        elif k == Keys.DOWN:        self.down()
        elif k == Keys.CTRL_u:      self.halfpage_up()
        elif k == Keys.CTRL_d:      self.halfpage_down()
        elif k == Keys.CTRL_UP:     flag, val = 'window_up', None
        elif k == Keys.CTRL_DOWN:   flag, val = 'window_down', None
        elif k == Keys.CTRL_g:      flag, val = 'hide_index', None
        elif k == Keys.ESC: # end search and get rid of results
            if self.searching:
                self.end_search()
                self.update_list()
                flag, val = 'end_search', None
            elif self.command_mode:
                self.end_command()
                flag, val = 'end_command', None
            elif self.preview:
                self.preview = False
                flag, val = 'end_preview', None
            else:
                self.update_list()
        elif k == Keys.RETURN: # end search and keep results
            if self.searching:
                ID = self.end_search()
                flag, val = 'end_search', ID
            elif self.command_mode:
                self.end_command()
                flag, val = 'exec_command', None
            else:
                flag, val = 'open', self.zett[self.row]['ID']
        elif self.searching:
            # only allow keys above this point while searching
            flag, val = 'searching', None
        elif self.command_mode:
            # only allow keys above this point in command mode
            flag, val = 'command', None
        elif k == ord('r'):         self.update_list()
        elif k == ord('o'): flag, val = 'open', self.zett[self.row]['ID']
        elif k == ord('e'): flag, val = 'edit', self.zett[self.row]['ID']
        elif k == ord('p'):
            if self.preview:
                self.preview = False
                flag, val = 'end_preview', None
            else:
                self.preview = True
                flag, val = 'start_preview', None
        elif k == ord('+'):         flag, val = 'new', None
        elif k == Keys.CTRL_n:      flag, val = 'new', None
        elif k == ord('/'):
            self.start_search()
            flag, val = 'start_search', None
        elif k == ord(':'):
            self.start_command()
            flag, val = 'start_command', None
        elif k == Keys.CTRL_q:      flag, val = 'quit', 'Index'

        return flag, val

    def up(self):
        if self.row > 0:
            self.row -= 1       # move cursor line up
        if self.top > self.row:
            self.top = self.row # scroll up if necessary
        self.refresh()

    def down(self):
        if self.row < len(self.zett) - 1:
            self.row += 1       # move cursor line down
        if self.top + self.rows - 1 < self.row:
            self.top = self.row - self.rows + 1 # scroll down if necessary
        self.refresh()

    def halfpage_up(self):
        self.row = max(self.row - curses.LINES//2, 0)
        if self.top > self.row:
            self.top = self.row # scroll up if necessary
        self.refresh()

    def halfpage_down(self):
        self.row = min(self.row + curses.LINES//2, len(self.zett)-1)
        if self.top + self.rows - 1 < self.row:
            self.top = self.row - self.rows + 1 # scroll down if necessary
        self.refresh()
