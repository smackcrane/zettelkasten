#!/bin/python3

############################################################################
#
#   zk.py
#       zettelkasten implementation in python
#
############################################################################

import curses
import time
import traceback
import utils
import config
from Keys import Keys
from WindowStack import WindowStack
from Index import Index
from Editor import Editor
from Viewer import Viewer
from StatusBar import StatusBar

def debugger(s='', log=None):
    if not log:
        log = config.logfile
    with open(log, 'a') as f:
        print(time.asctime(),file=f)
        print(s+'\n', file=f)

def main(screen):
    screen.refresh()
    # stack of windows/containers active on screen in order
    stack = WindowStack(screen)

    # create index window, not in window stack
    index = Index(curses.newwin(curses.LINES-1,curses.COLS))
    show_index = True   # flag to show index window or not
    # create status bar at bottom row, not in window stack
    status = StatusBar(curses.newwin( 1,curses.COLS, curses.LINES-1,0 ))

    # standard size for subwindows: at most quarter-screen, at most 20x70
    std_rows = min(20, curses.LINES//2)
    std_cols = min(70, curses.COLS//2)

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

            # debugger
            s = ''
            known_keys = Keys.__dict__
            for key in known_keys.keys():
                if known_keys[key] == k:
                    s = key
            if not s:
                s = chr(k)
            # leave this debugging out of commit
            #debugger(f'keypress:\t{s}')
            # end debugger

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
                y, x = stack.recommend(std_rows, std_cols)
                stack.push(Editor(
                    curses.newwin( std_rows,std_cols, y,x ),
                    config.kasten_dir+ID))
                show_index = False
            elif flag == 'edit':
                ID = val # expect val to be ID of zettel to edit
                # create an editor
                y, x = stack.recommend(std_rows, std_cols)
                stack.push(Editor(
                    curses.newwin( std_rows,std_cols, y,x ),
                    config.kasten_dir+ID))
                show_index = False
            elif flag == 'open':
                ID = val # expect val to be ID of zettel to edit
                # create a viewer
                y, x = stack.recommend(std_rows, std_cols)
                stack.push(Viewer(
                    curses.newwin( std_rows,std_cols, y,x ),
                    config.kasten_dir+ID))
                show_index = False
            elif flag == 'edit->open': # change editor to viewer
                ID, row = val # expect val to be list of ID and top row
                window = stack.pop().win
                rows, cols = window.getmaxyx()
                row = utils.convert_row(ID, cols, editor_row=row)
                stack.push(Viewer(window, config.kasten_dir+ID, row))
            elif flag == 'open->edit': # change viewer to editor
                ID, row = val # expect val to be list of ID and top row
                window = stack.pop().win
                rows, cols = window.getmaxyx()
                row = utils.convert_row(ID, cols, viewer_row=row)
                stack.push(Editor(window, config.kasten_dir+ID, row))
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
                instruction = status.exec_command()
                if instruction == 'count':
                    status.set(str(len(index.zett)))
                elif instruction == 'sort':
                    index.sort()
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
            debugger(f'error: {e}', log=config.logfile)
            status.debugger(state=True, log=config.logfile)
            index.debugger(state=True, log=config.logfile)
            stack.debugger(state=True, log=config.logfile, recursive=True)
            debugger(traceback.format_exc(), log=config.logfile)
        except KeyboardInterrupt:
            debugger(f'KeyboardInterrupt')
            status.error('KeyboardInterrupt: press any key to cancel, or KeyboardInterrupt again to quit')
            screen.getch() # not sure why two are needed, but doesn't
            screen.getch() # seem to work with just one?

if __name__ == '__main__':
    debugger('v'*15+'  START SESSION  '+'v'*15)
    curses.wrapper(main)
    debugger('^'*16+'  END SESSION  '+'^'*16)
