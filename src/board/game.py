import pygame, sys
from ai.CheckersAI import AI
from .logic import Logic
from .settings import *
from tkinter import messagebox


class Game:
    def __init__(self):
        self.logic = Logic()
        self.move_locked = False
        self.running = True
        self.winner = ""
        self.ai = AI('B')
        
    def countdown(self):
        countdown_seconds = 3  # Adjust as needed
        countdown_font = pygame.font.Font('assets/fonts/CascadiaCode.ttf', 100)
        
        while countdown_seconds > 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.draw_board()
            shadow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            shadow.fill((0, 0, 0, 100))
            self.screen.blit(shadow,(0,0))
            countdown_text = countdown_font.render(str(countdown_seconds), True, (255, 0, 0))
            self.screen.blit(countdown_text, (WIDTH // 2 - countdown_text.get_width() // 2, HEIGHT // 2 - countdown_text.get_height() // 2))
            pygame.display.flip()
            pygame.time.wait(1000)  # Wait one second
            countdown_seconds -= 1
    
    def display_winner(self):
        result = pygame.font.Font('assets/fonts/CascadiaCode.ttf', 50)
        self.draw_board()
        shadow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 100))
        self.screen.blit(shadow,(0,0))
        result_text = result.render(self.winner + " wins!", True, (255, 0, 0))
        self.screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, HEIGHT // 2 - result_text.get_height() // 2))
        pygame.display.flip()
        pygame.time.wait(3000)
        
    def set_winner(self):
        if self.logic.ndn == self.logic.ndb:
            self.winner = "Draw"
        else:
            if self.logic.ndn == 0 or self.logic.turn == 'B':
                self.winner = "White"
            elif self.logic.ndb == 0 or self.logic.turn == 'W':
                self.winner = "Black"

    def run(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('FISI_Checkers')
        self.clock = pygame.time.Clock()
        self.selected_piece = None
        
        self.draw_board()
        self.set_difficulty()
        self.countdown()

        while self.running:
            if self.logic.turn == 'B':
                self.handle_ai_move()
            if self.logic.is_game_over():
                self.set_winner()
                self.display_winner()
                self.running = messagebox.askyesno('Question','Do you want to play again?')
                if self.running:
                    self.logic.reset_board()
                    self.set_difficulty()
                    self.countdown()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_player_input()
            self.draw_board()
            pygame.display.flip()
            self.clock.tick(60)
        
    def handle_ai_move(self):
        if self.logic.turn == self.ai.color and not self.logic.is_game_over():
            ai_move = self.ai.get_best_move(self.logic)
            self.logic.make_move(ai_move)

    def handle_player_input(self):
        if self.logic.turn != self.ai.color:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            row = mouse_y // SQUARE_SIZE
            col = mouse_x // SQUARE_SIZE
            if self.selected_piece is None:
                piece = self.logic.board[row][col]
                if piece != ' ' and piece == self.logic.turn:
                    self.selected_piece = (row, col)
            else:
                start_row, start_col = self.selected_piece
                if (row, col) == self.selected_piece:
                    self.selected_piece = None
                elif self.logic.is_valid_capture(start_row, start_col, row, col):
                    self.logic.capture_piece(start_row, start_col, row, col)
                    if self.logic.turn == 'W':
                        self.logic.ndn -= 1
                    else: #self.logic.turn == 'B':
                        self.logic.ndb -= 1
                    
                    if self.logic.check_additional_capture(row, col):
                        self.move_locked = True
                        self.selected_piece = (row, col)
                        self.handle_player_input()
                    else:
                        self.switch_turn()
                        self.move_locked = False
                        self.selected_piece = None
                        
                elif self.logic.is_valid_move(start_row, start_col, row, col) and not self.move_locked:
                    self.logic.move_piece(start_row, start_col, row, col)
                    self.selected_piece = None
                    self.switch_turn()

    def set_difficulty(self):
        root = tk.Tk()
        root.withdraw()
        d = DifficultyDialog(root)
        if d.result == 'easy':
            self.ai.apply_difficulty(1)
        elif d.result == 'medium':
            self.ai.apply_difficulty(2)
        elif d.result == 'hard':
            self.ai.apply_difficulty(3)

    def switch_turn(self):
        self.logic.turn = 'W' if self.logic.turn == 'B' else 'B'

    def draw_board(self):
        for row in range(ROWS):
            for col in range(COLS):
                color = WHITE if (row + col) % 2 == 0 else BLACK
                pygame.draw.rect(self.screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                piece = self.logic.board[row][col]
                if piece != ' ':
                    piece_pos = (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2)
                    piece_img = black_checker_img if piece == 'B' else white_checker_img
                    piece_rect = piece_img.get_rect(center=piece_pos)
                    self.screen.blit(piece_img, piece_rect)
                    
        if self.selected_piece is not None:
            start_row, start_col = self.selected_piece
            selected_piece_image = b_selected_img if self.logic.board[start_row][start_col] == 'B' else w_selected_img
            selected_piece_rect = selected_piece_image.get_rect(center=(start_col * SQUARE_SIZE + SQUARE_SIZE // 2, start_row * SQUARE_SIZE + SQUARE_SIZE // 2))
            self.screen.blit(selected_piece_image, selected_piece_rect)
