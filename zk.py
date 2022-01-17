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


def main(screen):
    screen.refresh()
    # list of windows/containers active on screen in order
    wins = []

    # create table of contents window and add it to wins list
    wins.insert(0, Toc(curses.newwin(curses.LINES,curses.COLS)))

    while True:
        k = screen.getch()
        # pass keypress to active window
        # and capture possible additional instructions
        flag, val = wins[0].keypress(k)

        # TODO: pass control between windows, new and edit and quit
        if flag == 'new':
            # create new zettel
            ID = utils.new_zettel()
            # create an editor
            wins.insert(0, Editor(
                curses.newwin(
                        curses.LINES//2, curses.COLS,
                        curses.LINES//2, 0
                        ),
                config.kasten_dir+ID))
        elif flag == 'edit':
            pass
        elif flag == 'open':
            pass
        elif flag == 'quit':
            wins.pop(0)
            wins[0].refresh()


if __name__ == '__main__':
    curses.wrapper(main)
