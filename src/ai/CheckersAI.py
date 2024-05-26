#from board.game import Game
from board.logic import Logic            
from board.settings import ROWS, COLS
import random

class AI:
    def __init__(self, color):
        self.color = color  # Color of the AI player ('W' or 'B')
        self.depth = 6  # Depth of the Minimax search tree
        self.type = 0

    def get_best_move(self, logic):
        if self.type == 3:
            _, best_move = self.minimax(logic, self.depth, float('-inf'), float('inf'), True)
        if self.type == 2:
            best_move = self.greedy_best_move(logic)
        if self.type == 1:
            best_move = self.random_selection(logic)
            
        print("Best move: ", best_move)
        return best_move

    def minimax(self, logic, depth, alpha, beta, maximizing_player):
        if depth == 0 or logic.is_game_over():
            score =  self.evaluate(logic.board,logic.ndb, logic.ndn) # for debugging purposes
            #print (logic.actual_ai_move,":\t",score) # for debugging purposes
            return score, None

        if maximizing_player and logic.turn == 'B':
            max_eval = float('-inf')
            best_move = None
            movements = self.generate_moves(logic,'B')
            for move in movements:
                logic_copy = self.get_copy(logic)
                logic_copy.make_move(move)
                eval, _ = self.minimax(logic_copy, depth - 1, alpha, beta, False)
                #print (move,":\t",eval) # for debugging purposes
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            movements = self.generate_moves(logic,'W')
            for move in movements:
                logic_copy = self.get_copy(logic)
                logic_copy.make_move(move)
                eval, _ = self.minimax(logic_copy, depth - 1, alpha, beta, True)
                #print (move,":\t",eval) # for debugging purposes
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha cutoff
            return min_eval, best_move

    def greedy_best_move(self, logic):
        player = self.color
        movements = self.generate_moves(logic, player)
        best_move = None
        best_value = float('-inf') if player == 'B' else float('inf')
        
        for move in movements:
            logic_copy = self.get_copy(logic)
            logic_copy.make_move(move)
            eval = self.evaluate(logic_copy.board, logic_copy.ndb, logic_copy.ndn)
            print(f"Evaluating move {move}: {eval}")  # For debugging purposes

            if player == 'B':
                if eval > best_value:
                    best_value = eval
                    best_move = move
            else:
                if eval < best_value:
                    best_value = eval
                    best_move = move
        return best_move
    
    def random_selection(self, logic):
        return random.choice(self.generate_moves(logic, self.color))

    def generate_moves(self, logic, player):
        # Generate all possible moves for the AI player
        moves = []
        for row in range(ROWS):
            for col in range(COLS):
                if logic.board[row][col] == player:
                    if logic.locked_piece is not None and (row, col) != logic.locked_piece:
                        continue
                    for d_row, d_col in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                        if logic.is_valid_move(row, col, row + d_row, col + d_col) and not logic.locked:
                            moves.append((row, col, row + d_row, col + d_col))
                        elif logic.is_valid_capture(row, col, row + 2 * d_row, col + 2 * d_col):
                            moves.append((row, col, row + 2 * d_row, col + 2 * d_col))
                
        return moves

    def get_copy(self, logic):
        # Create a copy of the logic board
        copy_logic = Logic()
        copy_logic.board = [row[:] for row in logic.board]
        copy_logic.turn = logic.turn
        copy_logic.ndb = logic.ndb
        copy_logic.ndn = logic.ndn
        return copy_logic
    
    def evaluate(self, board, ndb, ndn):
        white_potential_captures = 0
        black_potential_captures = 0
        white_advance_bonus = 0
        black_advance_bonus = 0
        move_variety = set()
        for i in range(len(board)):
            for j in range(len(board[i])):
                piece = board[i][j]
                if piece == 'W':
                    if ((i > 1 and j > 1 and board[i-2][j-2] == ' ' and board[i-1][j-1] == 'B') or
                        (i > 1 and j < len(board[i]) - 2 and board[i-2][j+2] == ' ' and board[i-1][j+1] == 'B') or
                        (i < len(board) - 2 and j > 1 and board[i+2][j-2] == ' ' and board[i+1][j-1] == 'B') or
                        (i < len(board) - 2 and j < len(board[i]) - 2 and board[i+2][j+2] == ' ' and board[i+1][j+1] == 'B')):
                        white_potential_captures += 1
                    white_advance_bonus += (i + 1)
                    move_variety.add((i, j))
                elif piece == 'B':
                    if ((i > 1 and j > 1 and board[i-2][j-2] == ' ' and board[i-1][j-1] == 'W') or
                        (i > 1 and j < len(board[i]) - 2 and board[i-2][j+2] == ' ' and board[i-1][j+1] == 'W') or
                        (i < len(board) - 2 and j > 1 and board[i+2][j-2] == ' ' and board[i+1][j-1] == 'W') or
                        (i < len(board) - 2 and j < len(board[i]) - 2 and board[i+2][j+2] == ' ' and board[i+1][j+1] == 'W')):
                        black_potential_captures += 1
                    black_advance_bonus += (len(board) - i)
                    move_variety.add((i, j))
                    
        capture_difference = black_potential_captures - white_potential_captures
        piece_difference = ndn - ndb
        advance_bonus = black_advance_bonus - white_advance_bonus

        variety_penalty = 0
        if len(move_variety) < 5:  # Ajusta el umbral según la densidad del tablero
            variety_penalty = -2

        capture_weight = 0.3  # Para capturas
        advance_bonus_weight = 0.2  # Para avance
        penalty_weight = 0.1  # Para penalización de movimientos repetitivos

        result = 0.4*piece_difference + capture_weight * capture_difference + advance_bonus_weight * advance_bonus + penalty_weight * variety_penalty
        #print(f"potential captures: {black_potential_captures - white_potential_captures} | diferencia de fichas: {ndn - ndb}")
        return result
    
    def apply_difficulty(self, type):
        self.type = type
        
    def evaluate2(self, board, ndb, ndn):
        return (ndn - ndb)