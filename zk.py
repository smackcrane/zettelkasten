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
from StatusBar import StatusBar

def main(screen):
    screen.refresh()
    # stack of windows/containers active on screen in order
    stack = WindowStack(screen)

    # create index window, not in window stack
    index = Index(curses.newwin(curses.LINES-1,curses.COLS))
    show_index = True   # flag to show index window or not
    # create status bar at bottom row, not in window stack
    status = StatusBar(curses.newwin( 1,curses.COLS, curses.LINES-1,0 ))

    # standard size for subwindows: at most quarter-screen, at most 15x60
    rows = min(15, curses.LINES//3)
    cols = min(60, 3*curses.COLS//4)

    while True:
        try:    # general error handling
            # refresh screen
            if show_index:
                stack.refresh()
                index.refresh()
            else:
                index.refresh()
                stack.refresh()
            k = screen.getch()
            # pass keypress to active window
            # and capture possible additional instructions
            status.keypress(k)
            if stack and not show_index:
                flag, val = stack.keypress(k)
            else:
                flag, val = index.keypress(k)

            if flag == 'new':
                # create new zettel
                ID = utils.new_zettel()
                # create an editor
                y, x = stack.recommend(rows, cols)
                stack.push(Editor(
                    curses.newwin( rows,cols, y,x ),
                    config.kasten_dir+ID))
                show_index = False
            elif flag == 'edit':
                ID = val # expect val to be ID of zettel to edit
                # create an editor
                y, x = stack.recommend(rows, cols)
                stack.push(Editor(
                    curses.newwin( rows,cols, y,x ),
                    config.kasten_dir+ID))
                show_index = False
            elif flag == 'open':
                ID = val # expect val to be ID of zettel to edit
                # create a viewer
                y, x = stack.recommend(rows, cols)
                stack.push(Viewer(
                    curses.newwin( rows,cols, y,x ),
                    config.kasten_dir+ID))
                show_index = False
            elif flag == 'edit->open': # change editor to viewer
                ID = val # expect val to be ID of relevant zettel
                window = stack.pop().win
                stack.push(Viewer(window, config.kasten_dir+ID))
            elif flag == 'open->edit': # change viewer to editor
                ID = val # expect val to be ID of relevant zettel
                window = stack.pop().win
                stack.push(Editor(window, config.kasten_dir+ID))
            elif flag == 'show_index':
                show_index = True
            elif flag == 'hide_index':
                show_index = False
            elif flag == 'start_search':
                status.start_search()
                index.start_search()
            elif flag == 'end_search':
                status.end_search()
                index.end_search()
            elif flag == 'searching':
                if val == 'up':
                    index.up()
                    status.preview_ID(index.active_ID())
                elif val == 'down':
                    index.down()
                    status.preview_ID(index.active_ID())
                else:
                    index.search(status.search_text)
                if not show_index:
                    stack.refresh()
            elif flag == 'insert_link':
                status.end_search()
                ID = index.end_search()
                stack.wins[-1].insert_link(f'#{ID}')
            elif flag == 'start_command':
                status.start_command()
            elif flag == 'end_command':
                status.end_command()
            elif flag == 'exec_command':
                status.exec_command()
            elif flag == 'status':
                status.set(val) # set text in status bar
            elif flag == 'quit':
                if val == 'Index' and len(stack) > 1:
                    # don't kill index unless it's the last window
                    pass
                elif val == 'Index':
                    # if it is the last window, quit altogether
                    break
                else:
                    stack.pop()
            elif flag == 'window_up':
                if show_index:
                    show_index = False
                else:
                    stack.up()
                show_index = False
            elif flag == 'window_down':
                if show_index:
                    show_index = False
                else:
                    stack.down()
            elif flag == 'expand':
                stack.expand(val) # expect val = 'vertical', 'horizontal'
            elif flag == 'shrink':
                stack.shrink(val) # expect val = 'vertical', 'horizontal'
        except Exception as e:
            status.error(e)
        except KeyboardInterrupt:
            status.error('KeyboardInterrupt: press any key to cancel, or KeyboardInterrupt again to quit')
            screen.getch() # not sure why two are needed, but doesn't
            screen.getch() # seem to work with just one?

if __name__ == '__main__':
    curses.wrapper(main)
