#!/bin/python3

############################################################################
#
#   zk.py
#       zettelkasten implementation in python
#
############################################################################

import yaml
import curses
import datetime
import os

kasten_dir = "/home/sander/zettelkasten/kasten/"

zettel_template = {
        'TITLE': '',
        'BODY' : ''
        }

# entry point: list of IDs and titles
def list_zettel():
    IDs = os.listdir(path=kasten_dir)

    lines = []
    for ID in IDs:
        with open(kasten_dir+ID, 'r') as f:
            zettel = yaml.load(f, Loader=yaml.SafeLoader)
            lines += [{'ID': ID, 'LINE': ID+'  '+zettel['TITLE']}]
    return lines

# increment letters in IDs, a -> b -> ... -> z -> aa -> ab -> ...
def increment_letters(letters):
    # convert letters to list of numbers a=0, ..., z=25
    numbers = [ord(c)-97 for c in list(letters)][::-1]
    for i in range(len(numbers)):
        if numbers[i] < 25:
            numbers[i] += 1
            break
        else: # carry
            numbers[i] = 0
    else: # carried all the way through, need to add another letter
        numbers += [0]
    # convert back to letters
    letters = ''.join([chr(x+97) for x in numbers[::-1]])
    return letters
    
# create a new zettel
def new_zettel():
    # find correct ID: YYMMDD followed by a, b, ..., z, aa, ab, ...
    YYMMDD = datetime.date.today().isoformat().replace('-','')[2:]
    IDs = sorted(os.listdir(path=kasten_dir)) # is there a faster way?
    last = IDs[-1]
    if last[:6] == YYMMDD:
        # if it's the same YYMMDD as the last, increment letters
        letters = increment_letters(last[6:])
    ID = YYMMDD + letters

    # open template file for editing
    with open('/tmp/zettel.yaml', 'w') as f:
        yaml.dump(zettel_template, f)
    os.system('vim /tmp/zettel.yaml')
    os.system(f'mv /tmp/zettel.yaml {kasten_dir}{ID}')


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
            os.system(f'vim {kasten_dir}{ID}')
            self.refresh()


def curses_main(screen):
    boof = boofer(screen, [], curses.LINES, curses.COLS)
    boof.go()
    
    k = 0
    while k != ord('q'):
        k = screen.getch()
        boof.keypress(k)

if __name__ == '__main__':
    curses.wrapper(curses_main)
