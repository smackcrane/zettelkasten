############################################################################
#
#   WindowStack.py
#       basic methods for working with multiple overlapping curses windows
#
############################################################################

import curses
import numpy as np
import config
from Editor import Editor

# possible annoyance: everything breaks if self.wins is empty
class WindowStack:
    def __init__(self, screen):
        self.screen = screen
        # windows are stored in a list, index 0 at 'bottom' of stack
        self.wins = []
        # initialize density map of windows in screen
        rows, cols = screen.getmaxyx()
        self.dmap, self.window_density = self.initialize_densities( rows,cols )

    def initialize_densities(self, rows, cols):
        rows -= 1 # leave bottom row empty to keep status bar visible
        dmap = np.zeros((rows, cols), dtype=np.int64)

        # initialize density contribution of each new window
        density = lambda y,x: int(rows-y + cols-x)
        window_density = np.array(
                [[density(y,x) for x in range(cols)] for y in range(rows)],
                dtype=np.int64
                )
        #dmap += window_density # starting density
        return dmap, window_density

    def __len__(self):
        return len(self.wins)

    def debugger(self, s='', state=False, log=None, recursive=False):
        if not log:
            log = config.logfile
        with open(log, 'a') as f:
            print(s, file=f)
            if state:
                print(f'self.wins:\n{self.wins}\n\n'
                        + f'self.dmap:\n{self.dmap}\n\n',
                        file=f)
        if recursive:
            for window in self.wins:
                window.debugger(state=True, log=log)

    def refresh(self):
        if not self.wins: # if no windows, do nothing
            return
        # refresh windows from bottom to top
        for window in self.wins:
            window.refresh()
        # draw a box around top window
        y, x = self.wins[-1].getbegyx()
        rows, cols = self.wins[-1].getmaxyx()
        # adjust coordinates out by 1 if possible
        if y + rows + 1 < curses.LINES: rows += 1
        # strict inequality above because bottom row reserved for status bar
        if x + cols + 1 <= curses.COLS: cols += 1
        if y > 0:
            y -= 1
            if y + rows + 1 < curses.LINES: rows += 1
        if x > 0:
            x -= 1
            if x + cols + 1 <= curses.COLS: cols += 1
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
        self.dmap[y:y+rows, x:x+cols] -= self.window_density[:rows,:cols]
        self.refresh()
        return window

    # recommend coordinates for a new window
    # takes rows, cols dimensions for a new window
    # returns y, x upper-left coordinates for recommended placement
    def old_recommend(self, rows, cols):
        # compute mass of each rows x cols rectangle and choose the least
        # strat: taking cumulative sum of rows and then cumulative sum of 
        #   columns gives an array whose entries are cumulative sum of the
        #   rectangle between 0,0 and that entry
        rect_sums = self.dmap.cumsum(axis=0).cumsum(axis=1)
        # pad with zeros to get edges to work out
        #   np.r_ adds a row, np.c_ adds a column
        scr_rows, scr_cols = self.dmap.shape
        rect_sums = np.c_[
                np.zeros((scr_rows+1), dtype=np.int16),
                np.r_[ np.zeros((1,scr_cols), dtype=np.int16), rect_sums ]
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

    def recommend(self, rows, cols):
        density = self.window_density[:rows, :cols]
        scr_rows, scr_cols = self.dmap.shape
        candidate = [0,0]
        candidate_score = np.multiply(density, self.dmap[:rows,:cols]).sum()

        for x in range(scr_cols - cols + 1):
            for y in range(scr_rows - rows + 1):
                score = np.multiply(density, self.dmap[y:y+rows,x:x+cols]).sum()
                if score <= candidate_score:
                    candidate_score = score
                    candidate = [y,x]
        return candidate

    def up(self):
        self.wins.append(self.wins.pop(0))
        self.refresh()

    def down(self):
        self.wins.insert(0, self.wins.pop())
        self.refresh()

    def expand(self, direction):
        # note: helpful to go through WindowStack instead of doing directly
        #    in window in order to update dmap (using this push/pop)
        assert direction in ['vertical', 'horizontal'], \
                "invalid direction to expand"
        window = self.pop()
        y, x = window.getbegyx()
        rows, cols = window.getmaxyx()
        # add 3 to desired direction if possible
        if direction == 'vertical':
            top = min(1, y)
            # extra -1 for status bar at bottom row
            bottom = min(1, curses.LINES - y - rows - 1)
            y -= top
            rows += top + bottom
        elif direction == 'horizontal':
            left = min(2, x)
            right = min(2, curses.COLS - x - cols)
            x -= left
            cols += left + right
        window.resize( rows,cols, y,x )
        self.push(window)

    def shrink(self, direction):
        # note: helpful to go through WindowStack instead of doing directly
        #    in window in order to update dmap (using this push/pop)
        assert direction in ['vertical', 'horizontal'], \
                "invalid direction to expand"
        window = self.pop()
        y, x = window.getbegyx()
        rows, cols = window.getmaxyx()
        # subtract 3 from desired direction if possible
        # minimum size 10 rows x 40 columns
        if direction == 'vertical':
            top = max( min(1, rows - 10), 0) # max to ensure >= 0
            bottom = max( min(1, rows - top - 10), 0)
            y += top
            rows -= top + bottom
        elif direction == 'horizontal':
            left = max( min(2, cols - 40), 0)
            right = max( min(2, cols - left - 40), 0)
            x += left
            cols -= left + right
        window.resize( rows,cols, y,x )
        self.push(window)

    def resize(self, screen_rows, screen_cols):
        screen_rows -= 1 # leave bottom row empty to keep status bar visible
        old_wins = [win for win in self.wins]
        self.wins = []
        self.dmap, self.window_density = self.initialize_densities(
                                                screen_rows,screen_cols
                                                )
        self.debugger(state=True)
        for window in old_wins:
            y, x = window.getbegyx()
            rows, cols = window.getmaxyx()
            while y + rows > screen_rows - 1:
                # if the window goes off-screen, try moving up
                if y > 0:
                    y = max(0, screen_rows - rows - 1)
                # if we can't move up enough, also shrink
                else:
                    rows = min(rows, screen_rows - 1)
            while x + cols > screen_cols:
                # if the window goes off-screen, try moving left
                if x > 0:
                    x = max(0, screen_cols - cols)
                # if we can't move left enough, also shrink
                else:
                    cols = min(cols, screen_cols)
            window.resize( rows,cols, y,x )
            self.push(window)

    # check if ok to quit, failing if there is an editor window open
    def quit_ok(self):
        for win in self.wins:
            if isinstance(win, Editor):
                return False
        return True

    # return a list of zettel filepaths that are open
    def list_filepaths(self):
        return [win.filepath for win in self.wins]

    def keypress(self, k):
        return self.wins[-1].keypress(k)
