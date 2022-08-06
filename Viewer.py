############################################################################
#
#   Viewer.py
#       curses window (container) for viewing zettel
#
############################################################################

from ruamel import yaml
import curses
import re
import io
from contextlib import redirect_stdout
import sys
import os
import utils
from Keys import Keys
import config

class Viewer:
    def __init__(self, win, filepath, top=0):
        self.win = win # curses window we're living in
        self.rows, self.cols = self.win.getmaxyx() # dimensions of window
        self.filepath = filepath
        self.previous = [] # list of previous filepaths, to go back

        # keep track of which link cursor is on (default -1 means none)
        self.link = -1
        # top line of text visible
        self.top = top

        self.lines = [] # create variable initialized in self.load()
        self.links = [] # create variable initialized in self.load()
        self.load()
        self.refresh()

    def getbegyx(self):
        return self.win.getbegyx()

    def getmaxyx(self):
        return self.win.getmaxyx()

    def debugger(self, s='', state=False, log=None):
        if not log:
            log = '/dev/pts/1'
        with open(log, 'a') as f:
            print(s, file=f)
            if state:
                print(f'self.filepath: {self.filepath}\n'
                        + f'self.rows: {self.rows}\n'
                        + f'self.cols: {self.cols}\n'
                        + f'self.top: {self.top}\n',
                        file=f)
                print(self.lines, file=f)

    def load(self):
        try:
            # if the zettel has code, try to execute it and display results
            with open(self.filepath, 'r') as f:
                data = yaml.load(f, Loader=yaml.RoundTripLoader)
                assert 'CODE' in data, "if not then skip to except block"
                code = data['CODE']
                with io.StringIO() as out, redirect_stdout(out):
                    exec(code)
                    output = out.getvalue()
                data['CODE'] = output
                raw_lines = yaml.dump(
                                    data,
                                    Dumper=yaml.RoundTripDumper
                                    ).splitlines()
        except Exception as e:
            # load text from file as a list of lines
            #   then break into lines of window length
            with open(self.filepath, 'r') as f:
                raw_lines = f.readlines()
                raw_lines = [line.rstrip('\n') for line in raw_lines]
            # if there was an unknown error, add a message to end of zettel
            if type(e) != AssertionError:
                raw_lines.append(f'ERROR: {e}')
        self.lines = []
        line_lengths = [] # to translate between raw_lines and self.lines
        for line in raw_lines:
            if len(line) == 0: # special case for empty line
                line_lengths.append(1)
                self.lines.append('')
            else:
                line_lengths.append(-(len(line) // -self.cols)) # ceiling //
                for x in range(0, len(line), self.cols):
                    self.lines.append(line[x:x+self.cols])

        # create list of zk links, hyperlinks, and file links
        #   each a dict of ID(/url/filepath), start coords, and label
        ref = re.compile(r'#\d+[a-z]+')
        hyperref = re.compile(r'https?://\S+')
        fileref = re.compile(r'~/[-_a-zA-Z0-9/]+(\.|\*)[a-zA-Z]*')
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
            for link in hyperref.finditer(line):
                row = sum(line_lengths[:i]) + (link.start() // self.cols)
                col = link.start() % self.cols
                self.links.append({
                    'ID': link.group(),
                    'row': row,
                    'col': col,
                    'url': True
                    })
            for link in fileref.finditer(line):
                row = sum(line_lengths[:i]) + (link.start() // self.cols)
                col = link.start() % self.cols
                self.links.append({
                    'ID': link.group(),
                    'row': row,
                    'col': col,
                    'file': True
                    })
        # sort links by position in text
        self.links.sort(key=lambda l: [l['row'], l['col']])

        # search for backlinks
        my_ID = self.filepath.split('/')[-1]
        backlinks = utils.list_backlinks(my_ID)
        if backlinks:
            self.lines += ['','']
            row = sum(line_lengths) + 1 # keep track of row for self.links
            for ID in backlinks:
                row += 1
                title = utils.load_zettel(ID)['TITLE']
                # add to text and add to links
                self.lines.append(f'    <- #{ID} {title}')
                self.links.append({
                    'ID': '#'+ID,
                    'row': row,
                    'col': 7
                    })

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
        # move down if necessary to see the link
        l = self.links[self.link]
        bottom = l['row'] + ( (l['col']+len(l['ID'])-1) // self.cols )
        while self.top + self.rows <= bottom:
            self.top += 1
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
        # move up if necessary to see the link
        if self.top > self.links[self.link]['row']:
            self.top = self.links[self.link]['row']
        self.refresh()
        ID = self.links[self.link]['ID'].lstrip('#')
        title = utils.load_zettel(ID)['TITLE']
        flag, val = 'status', '#'+ID+' '+title
        return flag, val

    def open_link(self):
        # open active link for viewing
        if self.link == -1:
            return None, None
        link = self.links[self.link]
        if 'url' in link: # if it's a URL, open with firefox
            url = link['ID']
            os.system(f'firefox {url} >/dev/null 2>&1 &')
            return None, None
        elif 'file' in link: # if it's a file, try qpdfview
            path = link['ID']
            #assert path[-4:] in ['.jpg', '.png', '.pdf'], f"""
            #                    don't know how to open file {path}
            #                    """
            os.system(f'qpdfview {path} >/dev/null 2>&1 &')
            return None, None
        else: # if it's a zk link, pass back to zk.py to open
            ID = link['ID'].lstrip('#')
            flag, val = 'open', ID
            return flag, val

    # open new zettel in same window, closing previous zettel
    def go(self):
        # if no link is selected, do nothing
        if self.link == -1:
            return None, None
        link = self.links[self.link]
        # or if it's a url or file, do nothing
        if 'url' in link or 'file' in link:
            return None, None
        # at this point it should be a zk link
        ID = link['ID'].lstrip('#')
        # save old filepath, set new filepath, reload
        self.previous.append(self.filepath)
        self.filepath = config.kasten_dir+ID
        self.link = -1
        self.top = 0
        self.load()
        self.refresh()
        return None, None

    # back to previous zettel, reverse of go()
    def back(self):
        if not self.previous:
            # if no previous filepath, do nothing
            return None, None
        self.filepath = self.previous.pop()
        self.link = -1
        self.top = 0
        self.load()
        self.refresh()
        return None, None

    def resize(self, rows,cols, y,x ):
        oldwin = self.win
        self.win = curses.newwin( rows,cols, y,x )
        del oldwin
        self.rows, self.cols = self.win.getmaxyx()
        self.load()
        self.refresh()

    def keypress(self, k):
        flag, val = None, None
        if k == Keys.UP:            self.up()
        elif k == Keys.CTRL_u:
            for _ in range(10):
                self.up()
        elif k == Keys.DOWN:        self.down()
        elif k == Keys.CTRL_d:
            for _ in range(10):
                self.down()
        elif k == Keys.LEFT:        flag, val = self.left()
        elif k == Keys.RIGHT:       flag, val = self.right()
        elif k == Keys.RETURN:      flag, val = self.open_link()
        elif k == Keys.CTRL_g:      flag, val = 'show_index', None
        elif k == Keys.CTRL_n:      flag, val = 'new', None
        elif k == ord('+'):         flag, val = 'new', None
        elif k == Keys.CTRL_w:      flag, val = 'quit', None
        elif k == Keys.CTRL_q:      flag, val = 'quit', None
        elif k == Keys.CTRL_UP:     flag, val = 'window_up', None
        elif k == Keys.CTRL_DOWN:   flag, val = 'window_down', None
        elif k == ord('b'):         flag, val = self.back()
        elif k == ord('e'):
            ID = self.filepath.split('/')[-1] # extract ID from filepath
            flag, val = 'open->edit', [ID, self.top]
        elif k == ord('g'):         flag, val = self.go()
        elif k == ord('o'):         flag, val = self.open_link()
        elif k == ord('r'):
            self.load()
            self.refresh()
        elif k == Keys.CTRL_SHIFT_UP:    flag, val = 'expand', 'vertical'
        elif k == Keys.CTRL_SHIFT_DOWN:  flag, val = 'shrink', 'vertical'
        elif k == Keys.CTRL_SHIFT_RIGHT: flag, val = 'expand', 'horizontal'
        elif k == Keys.CTRL_SHIFT_LEFT:  flag, val = 'shrink', 'horizontal'

        return flag, val
