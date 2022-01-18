############################################################################
#
#   Viewer.py
#       curses window (container) for viewing zettel
#
############################################################################

import curses
import time
import sys
from Keys import Keys

class Viewer:
    def __init__(self, win, filepath):
        # curses window we're living in
        self.win = win
        # dimensions of window
        self.rows, self.cols = self.win.getmaxyx()
        # load text from file as a list of lines
        #   then break into lines of window length
        self.filepath = filepath
        with open(self.filepath, 'r') as f:
            lines = f.readlines()
        lines = [line.rstrip('\n') for line in lines] # strip newlines
        self.lines = []
        for line in lines:
            for x in range(0, len(line), self.cols):
                self.lines.append(line[x:x+self.cols])

        # top line of text visible
        self.top = 0

        self.refresh()

    def getbegyx(self):
        return self.win.getbegyx()

    def getmaxyx(self):
        return self.win.getmaxyx()

    def debug_log(self, s, state=False):
        debug_file = '/dev/pts/4'
        with open(debug_file, 'w') as f:
            print(s, file=f)
            if state:
                print(f'self.filepath: {self.filepath}\n'
                        + f'self.rows: {self.rows}\n'
                        + f'self.cols: {self.cols}\n'
                        + f'self.top: {self.top}\n',
                        file=f)
                print(self.lines, file=f)

    def refresh(self):
        self.win.erase()

        # i = row in self.lines, j = row in window
        for i in range(self.top, min(self.top+self.rows,len(self.lines))):
            j = i - self.top
            self.win.insstr( j,0, self.lines[i])
        # hide cursor
        curses.curs_set(0)

        self.win.refresh()

    # self.up/down/left/right just move relative to self.lines, cursor
    #   position and self.top are computed in self.refresh()
    def up(self):
        if self.top > 0:
            self.top -= 1
        self.refresh()

    def down(self):
        if self.top < len(self.lines)-self.rows:
            self.top += 1
        self.refresh()

    def left(self):
        pass

    def right(self):
        pass

    def enter(self):
        pass

    def keypress(self, k):
        flag, val = None, None
        if k == Keys.UP:            self.up()
        elif k == Keys.DOWN:        self.down()
        elif k == Keys.LEFT:        self.left()
        elif k == Keys.RIGHT:       self.right()
        elif k == Keys.RETURN:      self.enter()
        elif k == Keys.CTRL_q:      flag, val = 'quit', None
        elif k == Keys.CTRL_UP:     flag, val = 'window_up', None
        elif k == Keys.CTRL_DOWN:   flag, val = 'window_down', None

        return flag, val
