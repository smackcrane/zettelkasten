############################################################################
#
#   WindowStack.py
#       basic methods for working with multiple overlapping curses windows
#
############################################################################

import curses
import numpy as np

# possible annoyance: everything breaks if self.wins is empty
class WindowStack:
    def __init__(self, screen):
        self.screen = screen
        # windows are stored in a list, index 0 at 'bottom' of stack
        self.wins = []
        # initialize density map of windows in screen
        rows, cols = screen.getmaxyx()
        self.dmap = np.zeros((rows, cols))

        # initialize density contribution of each new window
        self.window_density = np.array(
                [[1/(1+i+j) for i in range(cols)] for j in range(rows)]
                )


    def __len__(self):
        return len(self.wins)

    def debugger(self, s, state=False):
        debug_file = '/dev/pts/3'
        with open(debug_file, 'w') as f:
            print(s, file=f)
            if state:
                print(f'self.wins:\n{self.wins}\n\n'
                        + f'self.dmap:\n{self.dmap}\n\n',
                        file=f)

    def refresh(self):
        # refresh windows from bottom to top
        for window in self.wins:
            window.refresh()
        # draw a box around top window
        y, x = self.wins[-1].getbegyx()
        rows, cols = self.wins[-1].getmaxyx()
        # adjust coordinates out by 1 if possible
        if y > 0: y -= 1
        if x > 0: x -= 1
        if y + rows + 2 < curses.LINES: rows += 2 # remember bottom row
        elif y + rows + 1 < curses.LINES: rows += 1 # is status bar
        if x + cols + 2 <= curses.COLS: cols += 2
        elif x + cols + 1 <= curses.COLS: cols += 1
        temp = curses.newwin( rows,cols, y,x )
        temp.border()
        temp.refresh()
        self.wins[-1].refresh()
        del temp

    def push(self, window):
        # add window to stack
        self.wins.append(window)
        # update density map, adding new weights to each pixel in the window
        y, x = window.getbegyx() # upper-left coordinates
        rows, cols = window.getmaxyx()
        self.dmap[y:y+rows, x:x+cols] += self.window_density[:rows,:cols]

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
        # pad with zeros to get edges to work out
        #   np.r_ adds a row, np.c_ adds a column
        scr_rows, scr_cols = self.dmap.shape
        rect_sums = np.c_[
                np.zeros((scr_rows+1)),
                np.r_[ np.zeros((1,scr_cols)), rect_sums ]
                ]
        # delete bottom row so we don't overlap the status bar that should
        #   be there
        rect_sums = rect_sums[:-1,:]
        # then to get the mass of any rectangle, use inclusion-exclusion
        #   bot/right-corner - u/r-corner - b/l-corner + u/l-corner
        # can do this all at once by slicing
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
