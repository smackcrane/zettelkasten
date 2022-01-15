############################################################################
#
#   Toc.py
#       table of contents curses window (container) for zettelkasten
#
############################################################################

import curses
import os
import yaml
import utils
from config import kasten_dir

class Toc:
    def __init__(self, win):
        # curses window we're living in
        self.win = win
        # dimensions of win (actually one less each)
        self.rows, self.cols = self.win.getmaxyx()
        # active 'cursor' row
        self.row = 0
        # top row in view
        self.top = 0
        
        # compile list of zettel IDs and titles
        self.zett = utils.list_IDs_titles()

        # make cursor invisible and move to start of active row
        curses.curs_set(0)

        self.refresh()

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
            self.win.addstr( j,0, self.zett[i]['TITLE'])
            if i == self.row:
                self.win.insstr( j,0, ' '*(9-len(self.zett[i]['ID'])))
                self.win.insstr( j,0, self.zett[i]['ID'], curses.A_REVERSE)
            else:
                self.win.insstr( j,0, self.zett[i]['ID'].ljust(9))
        self.win.refresh()

    def keypress(self, k):
        if k == curses.KEY_UP:      self.up()
        elif k == curses.KEY_DOWN:  self.down()
        elif k == ord('r'):         self.update_list()


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

