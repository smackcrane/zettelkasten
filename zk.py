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
from Editor import Editor

# class with methods for working with multiple overlapping curses windows
# TODO: everything broken if self.wins is empty
class WindowStack:
    def __init__(self):
        # windows are stored in a list, index 0 at 'bottom' of stack
        self.wins = []

    def refresh(self):
        for window in self.wins:
            window.refresh()

    def push(self, window):
        self.wins.append(window)
        self.refresh()

    def pop(self):
        self.wins.pop()
        self.refresh()

    def up(self):
        self.wins.append(self.wins.pop(0))
        self.refresh()

    def down(self):
        self.wins.insert(0, self.wins.pop())
        self.refresh()

    def keypress(self, k):
        flag, val = None, None
        if k == 566: # CTRL+up
            self.up()
        elif k == 525: # CTRL+down
            self.down()
        else:
            flag, val = self.wins[-1].keypress(k)
        return flag, val

def main(screen):
    screen.refresh()
    # stack of windows/containers active on screen in order
    stack = WindowStack()

    # create table of contents window and add it to wins stack
    stack.push(Toc(curses.newwin(curses.LINES,curses.COLS)))

    while True:
        k = screen.getch()
        # pass keypress to active window
        # and capture possible additional instructions
        flag, val = stack.keypress(k)

        # TODO: pass control between windows, new and edit and quit
        if flag == 'new':
            # create new zettel
            ID = utils.new_zettel()
            # create an editor
            stack.push(Editor(
                curses.newwin(
                        curses.LINES//2, curses.COLS,
                        curses.LINES//2, 0
                        ),
                config.kasten_dir+ID))
        elif flag == 'edit':
            ID = val # expect val to be ID of zettel to edit
            # create an editor
            stack.push(Editor(
                curses.newwin(
                        curses.LINES//2, curses.COLS,
                        curses.LINES//2, 0
                        ),
                config.kasten_dir+ID))
        elif flag == 'open':
            pass
        elif flag == 'quit':
            stack.pop()


if __name__ == '__main__':
    curses.wrapper(main)
