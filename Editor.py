############################################################################
#
#   Editor.py
#       curses window (container) for editing small text files
#
############################################################################

import curses
import time
import sys
from Keys import Keys
import config
import utils

class Editor:
    def __init__(self, win, filepath, row=0, col=0):
        # curses window we're living in
        self.win = win
        # load text from file as a list of lines (without trailing newlines)
        self.filepath = filepath
        with open(self.filepath, 'r') as f:
            self.lines = f.readlines() or [''] # in case of empty file
        self.lines = [ line.rstrip('\n') for line in self.lines ]
        # dimensions of window
        self.rows, self.cols = self.win.getmaxyx()

        # top line of text visible
        self.top = row
        # cursor position in self.lines (not in window)
        if row > 0:
            self.row = row
        else:
            self.row = 0
        self.col = col
        # hidden column for up/down btwn lines of different length
        self.hidden_col = col

        # flag for search in progress
        self.searching = False

        # clipboard for cutting and pasting, works as FIFO stack
        self.clipboard = []

        # attribute for display
        self.attr = curses.A_NORMAL

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
                print(f'self.rows: {self.rows}\n'
                        + f'self.cols: {self.cols}\n'
                        + f'self.row: {self.row}\n'
                        + f'self.col: {self.col}\n'
                        + f'self.top: {self.top}\n'
                        + f'self.lines: {self.lines}\n',
                        file=f)

    def start_search(self):
        self.searching = True

    def end_search(self):
        self.searching = False

    def refresh(self):
        self.win.erase()

        # first order of business: find self.top, top visible row
        # automatically scroll up if there are empty lines at the bottom
        #   and moving up a line would still fit
        if self.top > 0:
            buffer_rows = [
                    max(1, -(len(line) // -self.cols) ) # ceiling division
                    for line in self.lines[self.top-1:]
                    ]
            while sum(buffer_rows) <= self.rows:
                self.top -= 1
                if self.top == 0:
                    break
                buffer_rows.insert(0,
                        max(1, -(len(self.lines[self.top-1]) // -self.cols))
                        )
        if self.row > self.top:  # if too high, gotta worry about wraps
            # just worry about getting the whole current line on screen
            # NOTE: this won't work nice if current line overflows window
            # compute list of how many rows in window each line takes
            win_rows = [
                    max(1, -(len(line) // -self.cols) ) # ceiling division
                    for line in self.lines[self.top:self.row+1]
                    ]
            moves = 0
            # move down until it fits
            while sum(win_rows) > self.rows:
                win_rows.pop(0)
                moves += 1
            self.top += moves
            # check for edge case where cursor goes off the bottom
            if sum(win_rows) == self.rows:
                # current line goes to last row in window
                current_length = len(self.lines[self.row])
                if current_length % self.cols == 0 and current_length > 0:
                    # current line goes to last character in window
                    # gotta move down one more line
                    self.top += 1
        if self.row < self.top: # if top is too low, it's simple
            self.top = self.row # move up to active row

        # write lines and find cursor position
        # recall self.row, self.col is relative to self.lines, not window
        j = 0
        # i = row in self.lines, j = row in window
        for i in range(self.top, len(self.lines)):
            # if we're on self.row, we can compute the cursor position
            if i == self.row:
                y = j # row in window
                x = self.col # column in window
                # account for line wrapping
                while x >= self.cols:   # if we're wrapped
                    y += 1              # add one to row
                    x -= self.cols      # subtract a row's worth of columns
                # NOTE: as written we can error if there's a single line
                #   that fills past the whole window
            line = self.lines[i]
            # split into multiple chunks if longer than window
            chunks = [
                    line[x:x+self.cols]
                    for x in range(0,len(line),self.cols)
                    ]
            if not chunks:  # if empty line, chunks will be empty list
                j += 1      # still want to move forward a row
            for chunk in chunks:
                self.win.insstr( j,0, chunk, self.attr)
                j += 1
                # if we've filled the last row, break out of both loops
                if j > self.rows-1:
                    break
            if j > self.rows-1:
                break
        # move cursor into position
        curses.curs_set(1)
        try:
            self.win.move( y,x )
        except curses.error:
            # as noted above, if there's a single line that fills past the
            #   whole window, the current code will allow us to move outside
            #   the window and error
            pass

        self.win.refresh()

    def flash(self):
        # only flash if text is working attribute is normal
        if self.attr != curses.A_NORMAL:
            return
        self.attr = curses.A_REVERSE
        self.refresh()
        time.sleep(0.1)
        self.attr = curses.A_NORMAL
        self.refresh()

    # self.up/down/left/right just move relative to self.lines, cursor
    #   position and self.top are computed in self.refresh()
    def up(self):
        if self.row > 0:
            self.row -= 1
        # check if we're past the end of a line
        if self.col > len(self.lines[self.row]):
            self.col = len(self.lines[self.row])
        # or if we can go back to(wards) hidden_col
        elif self.col < self.hidden_col:
            self.col = min(self.hidden_col, len(self.lines[self.row]))
        self.refresh()

    def down(self):
        if self.row < len(self.lines)-1:
            self.row += 1
        # check if we're past the end of a line
        if self.col > len(self.lines[self.row]):
            self.col = len(self.lines[self.row])
        # or if we can go back to(wards) hidden_col
        elif self.col < self.hidden_col:
            self.col = min(self.hidden_col, len(self.lines[self.row]))
        self.refresh()

    def left(self):
        if self.col > 0:
            self.col -= 1
        self.hidden_col = self.col  # reset hidden_col
        self.refresh()

    def right(self):
        if self.col < len(self.lines[self.row]):
            self.col += 1
        self.hidden_col = self.col  # reset hidden_col
        self.refresh()

    def backward(self):
        # jump back a word (i.e. to the last space)
        col = self.lines[self.row].rfind(' ', 0, self.col)
        if col == -1: # if no space before self.col
            self.col = 0
            self.hidden_col = self.col
        else:
            self.col = col
            self.hidden_col = self.col
        self.refresh()

    def forward(self):
        # jump forward a word (i.e. to the next space)
        col = self.lines[self.row].find(' ', self.col+1)
        if col == -1:
            self.col = len(self.lines[self.row])-1
            self.hidden_col = self.col
        else:
            self.col = col
            self.hidden_col = self.col
        self.refresh()

    def line_beginning(self):
        self.col = 0
        self.hidden_col = self.col  # reset hidden_col
        self.refresh()

    def line_end(self):
        self.col = len(self.lines[self.row])
        self.hidden_col = self.col  # reset hidden_col
        self.refresh()

    def backspace(self):
        # if we're in the middle of a line
        if self.col > 0:
            self.lines[self.row] = self.lines[self.row][:self.col-1] \
                    + self.lines[self.row][self.col:]
            self.col -= 1   # move cursor
            self.hidden_col = self.col
        # if we're at the beginning of a line (not the first)
        elif self.row > 0:
            # pop the current line, move up a row and add it to that line
            line = self.lines.pop(self.row)
            self.row -= 1
            self.col = len(self.lines[self.row]) # move cursor
            self.hidden_col = self.col
            self.lines[self.row] += line
        self.refresh()

    def tab(self):
        # insert 4 spaces
        for _ in range(4):
            self.insert(Keys.SPACE)

    def newline(self):
        # split line in half
        first = self.lines[self.row][:self.col]
        second = self.lines[self.row][self.col:]
        # current line becomes first half
        self.lines[self.row] = first
        # move to next line and insert second half
        self.row += 1
        self.lines.insert(self.row, second)
        # move to beginning of line
        self.col = 0
        self.hidden_col = self.col
        self.refresh()

    def to_viewer(self):
        # check for changes by loading (& stripping) file text again
        with open(self.filepath, 'r') as f:
            file_text = f.readlines()
        file_text = [line.rstrip('\n') for line in file_text]
        # prompt if close without saving
        if self.lines != file_text:
            self.win.insstr(0,0," Close without saving? ",curses.A_REVERSE)
            self.win.refresh()
            k = self.win.getch()
            if k != Keys.CTRL_o: # anything but CTRL+o, go back
                self.refresh()
                flag, val = None, None
                return flag, val
        # if no changes or confirmed above, proceed to viewer
        ID = self.filepath.split('/')[-1] # extract ID from filepath
        flag, val = 'edit->open', [ID, self.top]
        return flag, val

    def close(self):
        # check for changes by loading (& stripping) file text again
        with open(self.filepath, 'r') as f:
            file_text = f.readlines()
        file_text = [line.rstrip('\n') for line in file_text]
        # prompt if close without saving
        if self.lines != file_text:
            self.win.insstr(0,0," Close without saving? ",curses.A_REVERSE)
            self.win.refresh()
            k = self.win.getch()
            if k != Keys.CTRL_w: # anything but CTRL+w, go back
                self.refresh()
                flag, val = None, None
                return flag, val
        # if no changes or confirmed above, proceed to close
        flag, val = 'close_window', None
        return flag, val

    def save(self):
        try:
            self.win.addstr(0,0," saving ... ",curses.A_REVERSE)
            self.win.refresh()
        except curses.error:
            pass
        with open(self.filepath, 'w') as f:
            f.write('\n'.join(self.lines) + '\n')
        if config.kasten_sync:
            try:
                self.win.addstr(0,0," syncing ... ",curses.A_REVERSE)
                self.win.refresh()
            except curses.error:
                pass
            utils.sync()
        self.flash()    # flash window to confirm
        self.refresh()

    def paste(self):
        if len(self.clipboard) > 0:
            # insert last elt of clipboard as new line after current line
            line = self.clipboard.pop()
            self.lines.insert(self.row + 1, line)
            # move down and up to work out cursor postiion
            self.down()
            self.up()

    def cut(self):
        # cut current line to clipboard
        line = self.lines.pop(self.row)
        self.clipboard.append(line)
        # work out line and cursor position
        if self.row == len(self.lines):
            self.up()
        elif self.row == len(self.lines) - 1:
            self.up()
            self.down()
        else:
            self.down()
            self.up()

    def insert(self, k):
        self.lines[self.row] = self.lines[self.row][:self.col] \
                + chr(k) \
                + self.lines[self.row][self.col:]
        self.col += 1
        self.hidden_col = self.col
        self.refresh()

    def insert_link(self, link):
        self.lines[self.row] = self.lines[self.row][:self.col] \
                + link \
                + self.lines[self.row][self.col:]
        self.col += len(link)
        self.hidden_col = self.col
        self.refresh()

    def resize(self, rows,cols, y,x ):
        oldwin = self.win
        self.win = curses.newwin( rows,cols, y,x )
        del oldwin
        self.rows, self.cols = self.win.getmaxyx()
        self.refresh()

    def keypress(self, k):
        flag, val = None, None
        if self.searching:  # only these commands allowed while searching
            if k == Keys.UP:        flag, val = 'searching', 'up'
            elif k == Keys.DOWN:    flag, val = 'searching', 'down'
            elif k == Keys.RETURN:
                self.end_search()
                flag, val = 'insert_link', None
            elif k == Keys.ESC:
                self.end_search()
                flag, val = 'end_search', None
            else:                   flag, val = 'searching', None
        # if not searching, normal commands apply
        elif k == Keys.UP:          self.up()
        elif k == Keys.DOWN:        self.down()
        elif k == Keys.LEFT:        self.left()
        elif k == Keys.RIGHT:       self.right()
        elif k == Keys.SHIFT_LEFT:  self.backward()
        elif k == Keys.SHIFT_RIGHT: self.forward()
        elif k == Keys.CTRL_a:      self.line_beginning()
        elif k == Keys.CTRL_e:      self.line_end()
        elif k == Keys.CTRL_f:
            self.start_search()
            flag, val = 'start_search', None
        elif k == Keys.CTRL_g:      flag, val = 'show_index', None
        elif k == Keys.BACKSPACE:   self.backspace()
        elif k == Keys.TAB:         self.tab()
        elif k == Keys.RETURN:      self.newline()
        elif k == Keys.ESC:
            self.save()
            flag, val = self.to_viewer()
        elif k == Keys.CTRL_d:
            for _ in range(10):
                self.down()
        elif k == Keys.CTRL_n:      flag, val = 'new', None
        elif k == Keys.CTRL_o:      flag, val = self.to_viewer()
        elif k == Keys.CTRL_q:      flag, val = 'quit', None
        elif k == Keys.CTRL_s:      self.save()
        elif k == Keys.CTRL_u:
            for _ in range(10):
                self.up()
        elif k == Keys.CTRL_v:      self.paste()
        elif k == Keys.CTRL_w:      flag, val = self.close()
        elif k == Keys.CTRL_x:      self.cut()
        elif k == Keys.CTRL_UP:     flag, val = 'window_up', None
        elif k == Keys.CTRL_DOWN:   flag, val = 'window_down', None
        elif k == Keys.CTRL_SHIFT_UP:    flag, val = 'expand', 'vertical'
        elif k == Keys.CTRL_SHIFT_DOWN:  flag, val = 'shrink', 'vertical'
        elif k == Keys.CTRL_SHIFT_RIGHT: flag, val = 'expand', 'horizontal'
        elif k == Keys.CTRL_SHIFT_LEFT:  flag, val = 'shrink', 'horizontal'
        else:                       self.insert(k)

        return flag, val
