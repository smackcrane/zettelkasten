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
from Index import Index
from Editor import Editor
from Viewer import Viewer

def main(screen):
    screen.refresh()
    # stack of windows/containers active on screen in order
    stack = WindowStack(screen)

    # create table of contents window and add it to wins stack
    stack.push(Index(curses.newwin(curses.LINES,curses.COLS)))

    # standard size for subwindows: at most quarter-screen, at most 15x60
    rows = min(15, curses.LINES//3)
    cols = min(60, 3*curses.COLS//4)

    while stack:
        k = screen.getch()
        # pass keypress to active window
        # and capture possible additional instructions
        flag, val = stack.keypress(k)

        if flag == 'new':
            # create new zettel
            ID = utils.new_zettel()
            # create an editor
            y, x = stack.recommend(rows, cols)
            stack.push(Editor(
                curses.newwin( rows,cols, y,x ),
                config.kasten_dir+ID))
        elif flag == 'edit':
            ID = val # expect val to be ID of zettel to edit
            # create an editor
            y, x = stack.recommend(rows, cols)
            stack.push(Editor(
                curses.newwin( rows,cols, y,x ),
                config.kasten_dir+ID))
        elif flag == 'open':
            ID = val # expect val to be ID of zettel to edit
            # create a viewer
            y, x = stack.recommend(rows, cols)
            stack.push(Viewer(
                curses.newwin( rows,cols, y,x ),
                config.kasten_dir+ID))
        elif flag == 'edit->open': # change editor to viewer
            ID = val # expect val to be ID of relevant zettel
            window = stack.pop().win
            stack.push(Viewer(window, config.kasten_dir+ID))
        elif flag == 'open->edit': # change viewer to editor
            ID = val # expect val to be ID of relevant zettel
            window = stack.pop().win
            stack.push(Editor(window, config.kasten_dir+ID))
        elif flag == 'quit':
            if val == 'Index' and len(stack) > 1:
                # don't kill index unless it's the last window
                pass
            else:
                stack.pop()
        elif flag == 'window_up':
            stack.up()
        elif flag == 'window_down':
            stack.down()

if __name__ == '__main__':
    curses.wrapper(main)
