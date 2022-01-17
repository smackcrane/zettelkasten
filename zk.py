#!/bin/python3

############################################################################
#
#   zk.py
#       zettelkasten implementation in python
#
############################################################################

import curses
import utils
import config
from WindowStack import WindowStack
from Toc import Toc
from Editor import Editor

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
        elif flag == 'window_up':
            stack.up()
        elif flag == 'window_down':
            stack.down()

if __name__ == '__main__':
    curses.wrapper(main)
