import pygame
import config as cfg
from game import Game
from snake import Snake

class UI:
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.snake_representation = []
        self.update_snake_representation()
        self.game_window = pygame.Rect(5, 5, 930, 890)
        self.food = pygame.Rect(0, 0, cfg.SNAKE_SIZE, cfg.SNAKE_SIZE)

        self.green = (0, 255, 0)
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.red = (255, 0, 0)

    # Creates the missing rectangles for self.snake_representation to match length of self.snake.body
    def update_snake_representation(self):
        if len(self.snake_representation) > len(self.game.snake.body):
            self.snake_representation = []

        for i in range(len(self.snake_representation), len(self.game.snake.body)):
            x_position = self.game.snake.body[i][0]
            y_position = self.game.snake.body[i][1]
            self.snake_representation.append(pygame.Rect(x_position, y_position, cfg.SNAKE_SIZE, cfg.SNAKE_SIZE))
    
    def update_snake_position(self):
        for i in range(len(self.snake_representation)):
            self.snake_representation[i].center = (self.game.snake.body[i][0], self.game.snake.body[i][1])
    
    def update_food_position(self):
        self.food.center = (self.game.food[0], self.game.food[1])

    def draw(self):
        self.update_snake_representation()
        self.update_snake_position()
        self.update_food_position()
        
        self.screen.fill(self.black)
        # Draw game window
        pygame.draw.rect(self.screen, self.white, self.game_window, width=3)
        
        # Draw Snake
        pygame.draw.rect(self.screen, self.red, self.snake_representation[0], width = 0)
        for i in range(1, len(self.snake_representation)):
            pygame.draw.rect(self.screen, self.white, self.snake_representation[i], width = 0)

        # Draw food
        pygame.draw.rect(self.screen, self.green, self.food, width = 0)

    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                self.game.handle_change_direction("up")
            elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                self.game.handle_change_direction("down")
            elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                self.game.handle_change_direction("right")
            elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                self.game.handle_change_direction("left")