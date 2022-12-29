"""The mechanics module implements the rules behind Conway's Game of Life"""

import random

class Board:
    """A Board object representing the state of the game using a 2D array
    
    Contains methods to compute the next state of the game, randomize the 
    board and set items to values. A value of 0 in self._state represents
    a dead cell, and a value of 1 represents an alive cell. \

    Attributes:
    _width -- width of the board
    _height -- height of the board
    _state -- current state of the game
    """

    def __init__(self, width=800, height=600):
        """Create a Board of size WIDTH x HEIGHT.

        width -- An integer; the width of the board; default is 800.
        height -- An integer; the height of the board; default is 600.
        """
        self._width = width
        self._height = height
        self._state = [ [0] * width for _ in range(height) ]
            
    def get_item(self, row, col):
        """Returns the item in position ROW, COL."""
        assert 0 <= row and row <= self._height \
            and 0 <= col and col <= self._width, "List index out of bounds"
        return self._state[row][col] 

    def set_item(self, row, col, value):
        """Sets the item in position ROW, COL equal to VALUE."""
        assert 0 <= row and row <= self._height \
            and 0 <= col and col <= self._width, "List index out of bounds"
        self._state[row][col] = value
    
    def randomize_board(self):
        """Randomly fills the board with alive and dead cells"""
        for i in range(self._height):
            for j in range(self._width):
                self._state[i][j] = random.randint(0,1)
        
    def count_alive_neighbors(self, row, col):
        """Returns the number of alive cells adjacent to ROW, COL

        Uses 8-cell Moore neighborhood to compute number of alive cells
        """
        assert 0 <= row and row <= self._height \
            and 0 <= col and col <= self._width, "List index out of bounds"
        count = 0

        # For computing the cell indexes of the 8 adjacent cells
        dr = [0, 0, 1, 1, 1, -1, -1, -1]
        dc = [-1, 1, -1, 0, 1, -1, 0, 1]
        for i in range(len(dr)):
            if (row + dr[i] < self._height and row + dr[i] >= 0 \
                and col + dc[i] < self._width and col + dc[i] >= 0):
                count += self._state[row + dr[i]][col + dc[i]]
        return count

    def next_state(self):
        """"Computes the next stage of the game using these simplified rules:

        1. If there is a dead cell with exactly 3 neighbors it becomes alive
        2. If there is an alive cell with 2 or 3 neighbors it stays alive
        3. All other cells are made dead (even if dead before)
        """
        newState = [ [0] * self._width for i in range(self._height) ]
        for i in range(self._height):
            for j in range(self._width):
                newState[i][j] = self._state[i][j]
        
        for i in range(self._height):
            for j in range(self._width):
                if self._state[i][j] == 1 and self.count_alive_neighbors(i,j) in [2,3]:
                    newState[i][j] = 1
                elif self._state[i][j] == 0 and self.count_alive_neighbors(i,j) == 3:
                    newState[i][j] = 1
                else:
                    newState[i][j] = 0
        self._state = newState
