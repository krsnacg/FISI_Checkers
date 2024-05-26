import pygame
import tkinter as tk
from tkinter import simpledialog

# Dimensiones del tablero y tamaño de los cuadrados
ROWS = COLS = 10
WIDTH, HEIGHT = 600, 600
SQUARE_SIZE = WIDTH // COLS

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Imagenes
black_checker_img = pygame.image.load('assets/img/b_checker.png')
white_checker_img = pygame.image.load('assets/img/w_checker.png')
b_selected_img = pygame.image.load('assets/img/b_checker1_selected.png')
w_selected_img = pygame.image.load('assets/img/w_checker1_selected.png')

black_checker_img = pygame.transform.scale(black_checker_img, (50, 50))
white_checker_img = pygame.transform.scale(white_checker_img, (50, 50))

# Difficulty
EASY = 'easy'
MEDIUM = 'medium'
HARD = 'hard'



class DifficultyDialog(simpledialog.Dialog):
        
    def body(self, master):
        tk.Label(master, text="Please select a difficulty:").pack()
        self.var = tk.StringVar(value="medium")
        self.radiobuttons = []
        for difficulty in ["easy", "medium", "hard"]:
            rb = tk.Radiobutton(master, text=difficulty, variable=self.var, value=difficulty)
            rb.pack(anchor="w")
            self.radiobuttons.append(rb)
        return self.radiobuttons[0]
    
    def change_result(self):
        if self.var.get() == "easy":
            self.result = EASY
        elif self.var.get() == "medium":
            self.result = MEDIUM
        elif self.var.get() == "hard":
            self.result = HARD

    def apply(self):
        self.result = self.var.get()
        self.change_result()