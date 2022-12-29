import sys
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView, QMainWindow, QPushButton, \
                            QGraphicsEllipseItem, QApplication, QVBoxLayout, QWidget, \
                            QHBoxLayout, QComboBox
from PyQt6.QtGui import QBrush, QColor, QPainter
from PyQt6.QtCore import Qt, QTimer
from mechanics import *

"""Global attributes:

DEAD_COLOR: QBrush to use for dead cells
ALIVE_COLOR: QBrush to use for alive cells
CELL_SIZE: integer representing the size of the cell in pixels
CANVAS_HEIGHT: height of the canvas
CANVAS_WIDTH: width of the canvas
"""
DEAD_COLOR = QBrush(QColor(0, 0, 0))
ALIVE_COLOR = QBrush(QColor(255, 165, 0))
CELL_SIZE = 6
CANVAS_HEIGHT = 660
CANVAS_WIDTH = 800

class Cell(QGraphicsEllipseItem):
    """A Cell object representing a single cell in the game

    Attributes:
    row -- y-coordinate of position
    col -- x-coordinate of position
    state -- a number 0 or 1, with 1 meaning alive and 0 meaning dead
    """
    def __init__(self, row, col, state = 0):
        """Create a Cell at position (ROW, COL) with state STATE.

        row -- An integer; the y-coordinate of position
        col -- An integer; the x-coordinate of position
        """
        assert state == 0 or state == 1, "State argument provided is invalid"

        super().__init__(0, 0, CELL_SIZE, CELL_SIZE)
        self.row = row
        self.col = col
        self.setPos(CELL_SIZE * self.row, CELL_SIZE * self.col)
        if state == 1:
            self.setBrush(ALIVE_COLOR)
        else:
            self.setBrush(DEAD_COLOR)

    def kill_cell(self):
        """Kills cell by changing it's color to DEAD_COLOR"""
        self.setBrush(DEAD_COLOR)
        self.update()
    
    def generate_cell(self):
        """Makes cell alive by changing it's color to ALIVE_COLOR"""
        self.setBrush(ALIVE_COLOR)
        self.update()


class Canvas(QGraphicsScene):
    """A Canvas object representing the full grid of cells to be used for 
    the game of life

    Attributes:
    width -- the width of the grid; this number represents the number of cells one \
        can fit horizontally across (NOT the screen width)
    height -- the height of the grid; this number represents the number of cells one \
        can fit vertically across (NOT the screen height)
    board -- a mechanics.Board object representing the current state of the game
    gui_board -- a 2D array of Cell objects corresponding with self.board
    game_paused -- a boolean representing whether the pause button has been hit; game \
        initially starts paused
    speed -- a number controlling how frequently the board is updated; higher means more \
        frequently
    update_timer -- a QTimer to update the Canvas every 800 / self.speed milliseconds
    """
    def __init__(self, width, height):
        """Create a Canvas of width WIDTH and height HEIGHT.

        width -- An integer; the width of the scene in pixels
        height -- An integer; the height of the scene in pixels
        """
        self.width = width // CELL_SIZE
        self.height = height // CELL_SIZE

        # Provided width and height are not used here to ensure there are no gaps 
        # at the edge of the board
        super().__init__(0, 0, self.height * CELL_SIZE, self.width * CELL_SIZE)
        self.board = Board(self.width, self.height)
        self.gui_board = [ [None] * self.width for _ in range(self.height) ]
        self.game_paused = True
        self.speed = 1

        # Add items to the canvas
        for i in range(self.height):
            for j in range(self.width):
                self.gui_board[i][j] = Cell(i, j, 0)
                self.addItem(self.gui_board[i][j])

        self.update_timer = QTimer(self)
        self.update_timer.setInterval(400)
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start()

    def toggle_pause(self):
        """Pauses the game if currently playing. Otherwise, plays the game"""
        self.game_paused = not self.game_paused
    
    def force_pause(self):
        """Pauses the game"""
        self.game_paused = True
    
    def change_speed(self, new_speed):
        """Change speed to NEW_SPEED"""
        self.speed = new_speed
    
    def randomize_game(self):
        """Randomize the state of the board. Maintains the correspondence with 
        self.board. Cells are never removed from canvas
        """
        self.board.randomize_board()
        for i in range(self.height):
            for j in range(self.width):
                if (self.board.get_item(i,j) == 1):
                    self.gui_board[i][j].generate_cell()
                else:
                    self.gui_board[i][j].kill_cell()
    
    def reset_game(self):
        """Kills all cells in self.gui_board and sets everything in self.board to 0"""
        for i in range(self.height):
            for j in range(self.width):
                self.gui_board[i][j].kill_cell()
                self.board.set_item(i, j, 0)
     
    def update(self):
        """Updates the game by first setting a new update interval. Checks if game is 
        paused before updating. Then updates gui_board
        """
        self.update_timer.setInterval(int(400 / self.speed))
        if self.game_paused:
            return
        self.board.next_state()
        for i in range(self.height):
            for j in range(self.width):
                if self.board.get_item(i, j) == 1:
                    self.gui_board[i][j].generate_cell()
                else:
                    self.gui_board[i][j].kill_cell()
    
    
    def mousePressEvent(self, e):
        """Handler for mouse press events. Left clicking a cell makes it alive
        and right clicking a cell kills it

        e -- A QGraphicsSceneMouseEvent to handle
        """
        if e.button() == Qt.MouseButton.LeftButton:
            point = e.buttonDownScenePos(Qt.MouseButton.LeftButton)
            row = int(point.x() // CELL_SIZE)
            col = int(point.y() // CELL_SIZE)
 
            self.gui_board[row][col].generate_cell()
            self.board.set_item(row, col, 1)
        elif e.button() == Qt.MouseButton.RightButton:
            point = e.buttonDownScenePos(Qt.MouseButton.RightButton)
            row = int(point.x() // CELL_SIZE)
            col = int(point.y() // CELL_SIZE)

            self.gui_board[row][col].kill_cell()
            self.board.set_item(row, col, 0)

class MainWindow(QMainWindow):
    """A MainWindow object that represents the complete gui with buttons and canvas

    Attributes:
    canvas -- A Canvas object to be added to the frame
    game -- A QGraphicsView object to render self.canvas
    pause_play_text -- A string to represent what the pause button text should say
    pause_button -- a QPushButton that allows user to pause/play game
    speeds -- a menu option for the speed at which to run the game
    playback_button -- a QComboBox that allows user to pause/play game
    randomize_button -- a QPushButton that allows user to randomize game and pause
    reset_button -- a QPushButton that allows user to clear board and pause
    """
    def __init__(self):
        """Create a MainWindow object for user interaction"""
        super(MainWindow, self).__init__()
        self.setWindowTitle("Conway's Game of Life")
        self.canvas = Canvas(CANVAS_HEIGHT, CANVAS_WIDTH)
        self.game = QGraphicsView(self.canvas)

        # Vectorizes graphics
        self.game.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        self.pause_play_text = "Play"

        self.pause_button = QPushButton()
        self.pause_button.clicked.connect(self.pause_game_button)
        self.pause_button.setText(self.pause_play_text)

        self.speeds = ['0.5x', '1x', '1.5x', '2x', '2.5x', '3x', '4x', '5x']

        self.playback_button = QComboBox()
        self.playback_button.addItems(self.speeds)
        self.playback_button.currentTextChanged.connect(self.playback_speed_button)
        self.playback_button.setCurrentIndex(1)


        self.randomize_button = QPushButton()
        self.randomize_button.clicked.connect(self.randomize_game_button)
        self.randomize_button.setText("Randomize")

        self.reset_button = QPushButton()
        self.reset_button.clicked.connect(self.reset_game_button)
        self.reset_button.setText("Clear")

        for button in [self.pause_button, self.playback_button, self.randomize_button, self.reset_button]:
            button.setStyleSheet("QPushButton::hover { background-color : #DD4814; }")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.randomize_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.playback_button)
        button_layout.addWidget(self.reset_button)

        full_layout = QVBoxLayout()
        full_layout.addWidget(QGraphicsView(self.canvas))
        full_layout.addLayout(button_layout)

        widget = QWidget()
        widget.setLayout(full_layout)
        self.setCentralWidget(widget)
    
    def pause_game_button(self):
        """Pauses/Plays the game depending on if the game is currently paused or not
        Also changes the text of the button from 'Pause' to 'Play' and vice versa
        """
        self.canvas.toggle_pause()
        if self.pause_play_text == "Pause":
            self.pause_play_text = "Play"
        else:
            self.pause_play_text = "Pause"
        self.pause_button.setText(self.pause_play_text)
    
    def reset_game_button(self):
        """Clears the board and forces the game to pause. Sets text of self.pause_button
        to 'Play'
        """
        self.canvas.reset_game()
        self.canvas.force_pause()
        self.pause_play_text = "Play"
        self.pause_button.setText(self.pause_play_text)
    
    def randomize_game_button(self):
        """Randomizes the board and forces the game to pause. Sets text of self.pause_button
        to 'Play'
        """
        self.canvas.randomize_game()
        self.canvas.force_pause()
        self.pause_play_text = "Play"
        self.pause_button.setText(self.pause_play_text)
    
    def playback_speed_button(self, text):
        """Modifies the speed of the game according to the selected speed option"""
        self.canvas.change_speed(float(str(text)[:-1]))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = MainWindow()
    view.show()
    app.exec()
