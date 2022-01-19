#!/bin/python3

############################################################################
#
#   WindowStack.py
#       basic methods for working with multiple overlapping curses windows
#
############################################################################

import numpy as np

# possible annoyance: everything breaks if self.wins is empty
class WindowStack:
    def __init__(self, screen):
        self.screen = screen
        # windows are stored in a list, index 0 at 'bottom' of stack
        self.wins = []
        # initialize density map of windows in screen
        rows, cols = screen.getmaxyx()
        self.dmap = np.zeros((rows, cols), np.int16)

    def __len__(self):
        return len(self.wins)

    def debug_log(self, s, state=False):
        debug_file = '/dev/pts/4'
        with open(debug_file, 'w') as f:
            print(s, file=f)
            if state:
                print(f'self.wins:\n{self.wins}\n\n'
                        + f'self.dmap:\n{self.dmap}\n\n',
                        file=f)

    def refresh(self):
        for window in self.wins:
            window.refresh()

    def push(self, window):
        # add window to stack
        self.wins.append(window)
        # update density map, adding 1 to each pixel in the window
        y, x = window.getbegyx() # upper-left coordinates
        rows, cols = window.getmaxyx()
        self.dmap[y:y+rows, x:x+cols] += 1

        self.refresh()

    def pop(self):
        window = self.wins.pop()
        # update density map, subtracting 1 from each pixel in the window
        y, x = window.getbegyx() # upper-left coordinates
        rows, cols = window.getmaxyx()
        self.dmap[y:y+rows, x:x+cols] -= 1
        self.refresh()
        return window

    # recommend coordinates for a new window
    # takes rows, cols dimensions for a new window
    # returns y, x upper-left coordinates for recommended placement
    def recommend(self, rows, cols):
        # compute mass of each rows x cols rectangle and choose the smallest
        # strat: taking cumulative sum of rows and then cumulative sum of 
        #   columns gives an array whose entries are cumulative sum of the 
        #   rectangle between 0,0 and that entry
        rect_sums = self.dmap.cumsum(axis=0).cumsum(axis=1)
        # then to get the mass of any rectangle, use inclusion-exclusion
        #   bot/right-corner - u/r-corner - b/l-corner + u/l-corner
        # can do this all at once by slicing
        # pad with zeros to get edges to work out; np.r_ adds a row,
        #   np.c_ adds a column
        scr_rows, scr_cols = self.dmap.shape
        rect_sums = np.c_[
                np.zeros((scr_rows+1), dtype=np.int16),
                np.r_[ np.zeros((1,scr_cols), dtype=np.int16), rect_sums ]
                ]
        mass = (
                rect_sums[rows:,cols:]      # bottom right corner
                - rect_sums[:-rows,cols:]   # upper right corner
                - rect_sums[rows:,:-cols]   # bottom left corner
                + rect_sums[:-rows,:-cols]  # upper left corner
                )
        # choose the smallest mass
        # favor bottom right, so go backwards (argmin returns first min)
        mass_rows, mass_cols = mass.shape
        index = (mass_rows * mass_cols - 1) - np.argmin(mass[::-1,::-1])
        y, x = divmod(index, mass_cols) # also argmin flattens, so unflatten
        return y, x


    def up(self):
        self.wins.append(self.wins.pop(0))
        self.refresh()

    def down(self):
        self.wins.insert(0, self.wins.pop())
        self.refresh()

    def keypress(self, k):
        return self.wins[-1].keypress(k)
