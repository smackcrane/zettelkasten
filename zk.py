#!/bin/python3

############################################################################
#
#   zk.py
#       zettelkasten implementation in python
#
############################################################################

import yaml
import curses
import os

kasten_dir = "/home/sander/zettelkasten/kasten/"

# entry point: list of IDs and titles
def list_zettel():
    IDs = os.listdir(path=kasten_dir)

    lines = []
    for ID in IDs:
        with open(kasten_dir+ID, 'r') as f:
            zettel = yaml.load(f, Loader=yaml.SafeLoader)
            lines += [{'ID': ID, 'LINE': ID+'  '+zettel['TITLE']}]
    return lines


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


def curses_main(screen):
    boof = boofer(screen, [], curses.LINES, curses.COLS)
    boof.go()
    
    k = 0
    while k != ord('q'):
        k = screen.getch()
        boof.keypress(k)

if __name__ == '__main__':
    curses.wrapper(curses_main)
