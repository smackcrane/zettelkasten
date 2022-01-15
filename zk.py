#!/bin/python3

############################################################################
#
#   zk.py
#       zettelkasten implementation in python
#
############################################################################

import yaml
import curses
from curses import textpad
import datetime
import os
import utils
import config
from Toc import Toc

'''
class boofer():
    def __init__(self, screen, data, rows, cols):
        self.screen = screen
        self.data = data
        self.lines = [item['LINE'] for item in data]
        self.rows = rows
        self.cols = cols

    def go(self):
        self.screen.clear()
        self.refresh()

    def refresh(self):
        self.data = list_zettel()
        self.lines = [item['LINE'] for item in self.data]
        row, col = self.screen.getyx()
        self.screen.clear()
        for i, item in enumerate(self.lines[:self.rows]):
            self.screen.addstr( i,0, item[:self.cols] )
        self.screen.move(row, col)

    def up(self):
        row, col = self.screen.getyx()
        if row > 0:
            row -= 1
            self.screen.move(row, col)
        self.refresh()

    def down(self):
        row, col = self.screen.getyx()
        if row < self.rows - 1:
            row += 1
            self.screen.move(row, col)
        self.refresh()

    def left(self):
        row, col = self.screen.getyx()
        if col > 0:
            col -= 1
            self.screen.move(row, col)
        self.refresh()

    def right(self):
        row, col = self.screen.getyx()
        if col < self.cols - 1:
            col += 1
            self.screen.move(row, col)
        self.refresh()

    def keypress(self, key):
        if key == curses.KEY_UP:
            self.up()
        elif key == curses.KEY_DOWN:
            self.down()
        elif key == curses.KEY_LEFT:
            self.left()
        elif key == curses.KEY_RIGHT:
            self.right()
        elif key == ord('+'): # add new zettel
            new_zettel()
            self.refresh()
        elif key == ord('e'): # edit zettel under cursor
            row, _ = self.screen.getyx()
            ID = self.data[row]['ID']
            os.system(f'vim {config.kasten_dir}{ID}')
            self.refresh()
'''

def main(screen):
    screen.refresh()
    # list of windows/containers active on screen in order
    wins = []

    # create table of contents window and add it to wins list
    wins.insert(0, Toc(curses.newwin(curses.LINES,curses.COLS)))

    while True:
        k = screen.getch()
        # handle special keys
        if k == 17: # CRTL+Q
            break
        elif k <= 26:
            pass
        elif k == ord('+'):
            # create new zettel
            ID = utils.new_ID()
            # open template for editing
            template = config.template.replace('YYMMDDxx', ID)
            # create a new window to edit in
            editor = curses.newwin(
                        curses.LINES//2, curses.COLS,
                        curses.LINES//2, 0
                        )
            editor.addstr( 0,0, template)
            curses.curs_set(1)
            tp = curses.textpad.Textbox(editor)
            contents = tp.edit()
            # write to file
            with open(config.kasten_dir+ID, 'w') as f:
                f.write(contents)
            # remove editing window
            del editor
            curses.curs_set(0)
        else: # otherwise pass on keypress to active window
            wins[0].keypress(k)

if __name__ == '__main__':
    curses.wrapper(main)
