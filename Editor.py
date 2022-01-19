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

class Editor:
    def __init__(self, win, filepath, row=0, col=0):
        # curses window we're living in
        self.win = win
        # load text from file as a list of lines (without trailing newlines)
        self.filepath = filepath
        with open(self.filepath, 'r') as f:
            self.lines = f.readlines()
        self.lines = [ line.rstrip('\n') for line in self.lines ]
        # dimensions of window
        self.rows, self.cols = self.win.getmaxyx()

        # top line of text visible
        self.top = 0
        # cursor position in self.lines (not in window)
        self.row, self.col = row, col
        # hidden column for up/down btwn lines of different length
        self.hidden_col = col

        # attribute for display
        self.attr = curses.A_NORMAL

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
                print(f'self.rows: {self.rows}\n'
                        + f'self.cols: {self.cols}\n'
                        + f'self.row: {self.row}\n'
                        + f'self.col: {self.col}\n'
                        + f'self.top: {self.top}\n',
                        file=f)

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
            while sum(buffer_rows) < self.rows:
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
                if len(self.lines[self.row]) % self.cols == 0:
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
        except:
            # as noted above, if there's a single line that fills past the
            #   whole window, the current code will allow us to move outside
            #   the window and error
            # for the moment just reset to something that won't error
            self.col, self.hidden_col = 0,0
            self.win.move(0,0)

        self.win.refresh()

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

    def quit(self):
        # check for changes by loading (& stripping) file text again
        with open(self.filepath, 'r') as f:
            file_text = f.readlines()
        file_text = [line.rstrip('\n') for line in file_text]
        # prompt if quit without saving
        if self.lines != file_text:
            self.win.insstr(0,0," Quit without saving? ",curses.A_REVERSE)
            self.win.refresh()
            k = self.win.getch()
            if k != 17: # anything but CTRL+q, go back
                self.refresh()
                flag, val = None, None
                return flag, val
        # if no changes or confirmed above, proceed to quit
        # by returning flag to that effect
        flag, val = 'quit', None
        return flag, val

    def save(self):
        with open(self.filepath, 'w') as f:
            f.write('\n'.join(self.lines))
        # flash window to confirm
        self.attr = curses.A_REVERSE
        self.refresh()
        time.sleep(0.1)
        self.attr = curses.A_NORMAL
        self.refresh()

    def insert(self, k):
        self.lines[self.row] = self.lines[self.row][:self.col] \
                + chr(k) \
                + self.lines[self.row][self.col:]
        self.col += 1
        self.hidden_col = self.col
        self.refresh()

    def keypress(self, k):
        flag, val = None, None
        if k == Keys.UP:            self.up()
        elif k == Keys.DOWN:        self.down()
        elif k == Keys.LEFT:        self.left()
        elif k == Keys.RIGHT:       self.right()
        elif k == Keys.CTRL_a:      self.line_beginning()
        elif k == Keys.CTRL_e:      self.line_end()
        elif k == Keys.BACKSPACE:   self.backspace()
        elif k == Keys.TAB:         self.tab()
        elif k == Keys.RETURN:      self.newline()
        elif k == Keys.CTRL_o:
            ID = self.filepath.split('/')[-1] # extract ID from filepath
            flag, val = 'edit->open', ID
        elif k == Keys.CTRL_q:      flag, val = self.quit()
        elif k == Keys.CTRL_s:      self.save()
        elif k == Keys.CTRL_w:      self.save()
        elif k == Keys.CTRL_UP:     flag, val = 'window_up', None
        elif k == Keys.CTRL_DOWN:   flag, val = 'window_down', None
        else:                       self.insert(k)

        return flag, val
