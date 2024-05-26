import random
from .settings import ROWS, COLS

class Logic:
    def __init__(self):
        self.reset_board()
        
    def initialize_board(self):
        for row in range(ROWS):
            for col in range(COLS):
                # Place black pieces on dark squares in the first three rows
                if row % 2 != col % 2 and row < 3:
                    self.board[row][col] = 'B'
                # Place white pieces on dark squares in the last three rows
                elif row % 2 != col % 2 and row > ROWS - 4:
                    self.board[row][col] = 'W'

    def reset_board(self):
        self.board = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        #self.turn = "B"  # Assume black starts
        if random.randint(0, 1): # Randomly select the starting player
            self.turn = "W"
        else:
            self.turn = "B"
        self.ndb = 15
        self.ndn = 15
        self.locked = False
        self.locked_piece = None
        self.actual_ai_move = None # for debugging purposes
        self.initialize_board()

    def is_valid_move(self, start_row, start_col, end_row, end_col):
        # Check if the move is within the bounds of the board
        if not (0 <= end_row < ROWS and 0 <= end_col < COLS):
            return False
        # Check if the end position is empty
        if self.board[end_row][end_col] != ' ':
            return False
        # Check if the move is diagonal and only one square away
        if abs(start_col - end_col) != 1 or abs(start_row - end_row) != 1:
            return False
        # Check the direction of movement based on the checker's color
        if self.board[start_row][start_col] == 'B' and end_row <= start_row:
            return False  # Black checkers can only move downwards
        if self.board[start_row][start_col] == 'W' and end_row >= start_row:
            return False  # White checkers can only move upwards
        return True

    def is_valid_capture(self, start_row, start_col, end_row, end_col):
        # Check if the move is within the bounds of the board
        if not (0 <= end_row < ROWS and 0 <= end_col < COLS):
            return False
        # Check if the end position is empty
        if self.board[end_row][end_col] != ' ':
            return False
        # Check if the move is diagonal and exactly two squares away
        if abs(start_row - end_row) != 2 or abs(start_col - end_col) != 2:
            return False
        # Check if there is an opponent piece to capture
        mid_row = (start_row + end_row) // 2
        mid_col = (start_col + end_col) // 2
        if self.board[mid_row][mid_col] == ' ':
            return False
        # Check if the opponent piece is of the opposite color
        if self.board[mid_row][mid_col] == self.turn:
            return False
        return True

    def check_additional_capture(self, start_row, start_col):
        # Define the four diagonal directions
        diagonal_directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        # Iterate through each diagonal direction
        for dr, dc in diagonal_directions:
            # Calculate the position of the adjacent square in the diagonal direction
            adj_row, adj_col = start_row + dr, start_col + dc
            # Calculate the position of the capture square in the diagonal direction
            capture_row, capture_col = start_row + 2*dr, start_col + 2*dc
            # Check if the capture square is within the board bounds
            if 0 <= capture_row < ROWS and 0 <= capture_col < COLS:
                # Check if the adjacent square contains an opponent piece and the capture square is empty
                if self.turn == 'B' and self.board[adj_row][adj_col] == 'W' and self.board[capture_row][capture_col] == ' ':
                    return True
                elif self.turn == 'W' and self.board[adj_row][adj_col] == 'B' and self.board[capture_row][capture_col] == ' ':
                    return True
                #if self.board[adj_row][adj_col] in ('W', 'B') and self.board[capture_row][capture_col] == ' ':
                    return True  # Additional capture is possible
        return False  # No additional captures are possible

    def move_piece(self, start_row, start_col, end_row, end_col):
        self.board[end_row][end_col] = self.board[start_row][start_col]
        self.board[start_row][start_col] = ' '

    def capture_piece(self, start_row, start_col, end_row, end_col):
        mid_row = (start_row + end_row) // 2
        mid_col = (start_col + end_col) // 2
        self.board[end_row][end_col] = self.board[start_row][start_col]
        self.board[mid_row][mid_col] = ' '
        self.board[start_row][start_col] = ' '
        
    def is_game_over(self):
        return self.ndb == 0 or self.ndn == 0 or not self.is_movement_available()
    
    def make_move(self, move):
        #print("Making move: ", move)
        self.actual_ai_move = move
        start_row, start_col, end_row, end_col = move
        if self.is_valid_capture(start_row, start_col, end_row, end_col):
            self.capture_piece(start_row, start_col, end_row, end_col)
            # Decrement the number of pieces of the captured player
            if self.turn == 'W':
                self.ndn -= 1
            else: #self.logic.turn == 'B':
                self.ndb -= 1
            if self.check_additional_capture(end_row, end_col):  # Check for additional captures after the first capture
                self.locked = True  # Lock the turn until all captures are completed
                self.locked_piece = (end_row, end_col)  # Store the piece that made the capture
            else:
                self.locked = False # Unlock the turn if no additional captures are possible
                self.turn = 'W' if self.turn == 'B' else 'B' # Switch turn after capture
                self.locked_piece = None
        elif self.is_valid_move(start_row, start_col, end_row, end_col) and not self.locked:
            self.move_piece(start_row, start_col, end_row, end_col)
            self.turn = 'W' if self.turn == 'B' else 'B'  # Switch turn after move
        else:
            raise ValueError("Invalid move")
        
    def is_movement_available(self):
        for row in range(ROWS):
            for col in range(COLS):
                if self.board[row][col] == self.turn:
                    if self.locked_piece is not None and (row, col) != self.locked_piece:
                        continue
                    for d_row, d_col in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                        if self.is_valid_move(row, col, row + d_row, col + d_col) and not self.locked:
                            return True
                        elif self.is_valid_capture(row, col, row + 2 * d_row, col + 2 * d_col):
                            return True
        return False