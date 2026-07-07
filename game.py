import config as cfg
from snake import Snake
import random

class Game:
    def __init__(self):
        self.snake = Snake()
        self.game_window_edges = [5, 935, 5, 895]
        self.food = [cfg.SNAKE_SIZE * random.randint(1, 46), cfg.SNAKE_SIZE * random.randint(1, 44)]
    
    def outside_game_window(self, x, y):
        return x < self.game_window_edges[0] or x > self.game_window_edges[1] or y < self.game_window_edges[2] or y > self.game_window_edges[3]  
    
    def inside_food(self, x, y):
        return x == self.food[0] and y == self.food[1]
    
    def handle_food_eaten(self, snake):
        self.snake.add_body_parts(1)
        self.food = [cfg.SNAKE_SIZE * random.randint(1, 46), cfg.SNAKE_SIZE * random.randint(1, 44)]

    def reset_snake(self):
        self.snake.body[0] = [460, 460]

    def update_game(self):
        self.snake.move()
        if self.outside_game_window(self.snake.body[0][0], self.snake.body[0][1]):
            self.reset_snake()
        elif self.inside_food(self.snake.body[0][0], self.snake.body[0][1]):
            self.handle_food_eaten(self.snake)
