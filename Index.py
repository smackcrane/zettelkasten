############################################################################
#
#   Index.py
#       table of contents curses window (container) for zettelkasten
#
############################################################################

import curses
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
        
        # compile list of zettel IDs and titles
        self.zett = utils.list_IDs_titles()

        # make cursor invisible
        curses.curs_set(0)

        self.refresh()

    def getbegyx(self):
        return self.win.getbegyx()

    def getmaxyx(self):
        return self.win.getmaxyx()

    def update_list(self):
        self.zett = utils.list_IDs_titles()
        self.refresh()

    def refresh(self):
        self.win.erase()
        # for each visible line
        for i in range(self.top, min(self.top+self.rows+1, len(self.zett))):
            # i = row in zettel list, j = row in window
            j = i - self.top
            # add ID and title, highlighting ID on active row
            if self.zett[i]['TITLE']: # allow None title without error
                self.win.addstr( j,0, self.zett[i]['TITLE'])
            if i == self.row:
                self.win.insstr( j,0, ' '*(9-len(self.zett[i]['ID'])))
                self.win.insstr( j,0, self.zett[i]['ID'], curses.A_REVERSE)
            else:
                self.win.insstr( j,0, self.zett[i]['ID'].ljust(9))
        curses.curs_set(0) # hide cursor
        self.win.refresh()

    def keypress(self, k):
        flag, val = None, None
        if k == Keys.UP:      self.up()
        elif k == Keys.DOWN:  self.down()
        elif k == ord('r'):         self.update_list()
        elif k == ord('o'): flag, val = 'open', self.zett[self.row]['ID']
        elif k == ord('e'): flag, val = 'edit', self.zett[self.row]['ID']
        elif k == ord('+'): flag, val = 'new', None
        elif k == Keys.CTRL_UP:  flag, val = 'window_up', None
        elif k == Keys.CTRL_DOWN:  flag, val = 'window_down', None

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
        if self.top < self.row - self.rows:
            self.top = self.row - self.rows # scroll down if necessary
        self.refresh()
