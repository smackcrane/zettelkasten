#!/bin/python3

############################################################################
#
#   WindowStack.py
#       basic methods for working with multiple overlapping curses windows
#
############################################################################

# possible annoyance: everything breaks if self.wins is empty
class WindowStack:
    def __init__(self):
        # windows are stored in a list, index 0 at 'bottom' of stack
        self.wins = []

    def refresh(self):
        for window in self.wins:
            window.refresh()

    def push(self, window):
        self.wins.append(window)
        self.refresh()

    def pop(self):
        self.wins.pop()
        self.refresh()

    def up(self):
        self.wins.append(self.wins.pop(0))
        self.refresh()

    def down(self):
        self.wins.insert(0, self.wins.pop())
        self.refresh()

    def keypress(self, k):
        return self.wins[-1].keypress(k)
