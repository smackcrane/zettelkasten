############################################################################
#
#   Viewer.py
#       curses window (container) for viewing zettel
#
############################################################################

import curses
import re
import time
import sys
import utils
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
            raw_lines = f.readlines()
        raw_lines = [line.rstrip('\n') for line in raw_lines]
        self.lines = []
        line_lengths = [] # to translate between raw_lines and self.lines
        for line in raw_lines:
            line_lengths.append(-(len(line) // -self.cols)) # ceiling div
            for x in range(0, len(line), self.cols):
                self.lines.append(line[x:x+self.cols])

        # create list of links, each a dict of ID and start coords
        ref = re.compile(r'#\d+[a-z]+')
        self.links = []
        for i, line in enumerate(raw_lines):
            for link in ref.finditer(line):
                row = sum(line_lengths[:i]) + (link.start() // self.cols)
                col = link.start() % self.cols
                self.links.append({
                    'ID': link.group(),
                    'row': row,
                    'col': col
                    })
        # keep track of which link cursor is on (default -1 means none)
        self.link = -1

        # top line of text visible
        self.top = 0

        self.refresh()

    def getbegyx(self):
        return self.win.getbegyx()

    def getmaxyx(self):
        return self.win.getmaxyx()

    def debugger(self, s, state=False):
        log_file = '/dev/pts/1'
        with open(log_file, 'w') as f:
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
        # underline links
        for i, link in enumerate(self.links):
            # assume a link is broken over at most two lines
            breakpt = self.cols - link['col']
            if i == self.link: # highlight link under cursor
                attr = curses.A_REVERSE
            else: # underline links in general
                attr = curses.A_UNDERLINE
            row = link['row'] - self.top
            try:
                if 0 <= row < self.rows:
                    self.win.addstr( row,link['col'],
                            link['ID'][:breakpt], attr )
                if 0 <= row + 1 < self.rows:
                    self.win.addstr( row+1,0,
                            link['ID'][breakpt:], attr )
            except:     # painting the lower right corner raises error
                pass    # but only after painting, so just ignore error
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
        if not self.links or self.link == -1:
            return None, None # if no links or no active link, do nothing
        if self.link > 0:
            self.link -= 1
        # move up if necessary to see the link
        if self.top > self.links[self.link]['row']:
            self.top = self.links[self.link]['row']
        self.refresh()
        ID = self.links[self.link]['ID'].lstrip('#')
        title = utils.load_zettel(ID)['TITLE']
        flag, val = 'status', '#'+ID+' '+title
        return flag, val

    def right(self):
        if not self.links: # if no links, do nothing
            return None, None
        if self.link < len(self.links) - 1:
            self.link += 1
        # move down if necessary to see the link
        l = self.links[self.link]
        bottom = l['row'] + ( (l['col']+len(l['ID'])-1) // self.cols )
        while self.top + self.rows <= bottom:
            self.top += 1
        self.refresh()
        ID = self.links[self.link]['ID'].lstrip('#')
        title = utils.load_zettel(ID)['TITLE']
        flag, val = 'status', '#'+ID+' '+title
        return flag, val

    def enter(self):
        # open active link for viewing
        if self.link == -1:
            return None, None
        ID = self.links[self.link]['ID'].lstrip('#')
        flag, val = 'open', ID
        return flag, val

    def keypress(self, k):
        flag, val = None, None
        if k == Keys.UP:            self.up()
        elif k == Keys.DOWN:        self.down()
        elif k == Keys.LEFT:        flag, val = self.left()
        elif k == Keys.RIGHT:       flag, val = self.right()
        elif k == Keys.RETURN:      flag, val = self.enter()
        elif k == Keys.CTRL_q:      flag, val = 'quit', None
        elif k == Keys.CTRL_UP:     flag, val = 'window_up', None
        elif k == Keys.CTRL_DOWN:   flag, val = 'window_down', None
        elif k == ord('e'):
            ID = self.filepath.split('/')[-1] # extract ID from filepath
            flag, val = 'open->edit', ID

        return flag, val
