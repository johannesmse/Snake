import pygame
import config as cfg
from game import Game
from snake import Snake

class UI:
    def __init__(self, screen, game, agent):
        self.screen = screen
        self.game = game
        self.snake = game.snake
        self.snake_representation = []
        self.update_snake_representation()
        self.game_window = pygame.Rect(0, 0, cfg.GAME_WINDOW_WIDTH, cfg.GAME_WINDOW_HEIGHT)
        self.menu_window = pygame.Rect(cfg.MENU_START_X, 0, cfg.MENU_WINDOW_WIDTH, cfg.MENU_WINDOW_HEIGHT)
        self.food = pygame.Rect(0, 0, cfg.SNAKE_SIZE, cfg.SNAKE_SIZE)

        self.score_font = pygame.font.SysFont(None, 24)
        

        self.green = (0, 255, 0)
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.red = (255, 0, 0)
        self.grey = (54, 69, 79)

        self.agent = agent
        self.display_setting = None

    # Creates the missing rectangles for self.snake_representation to match length of self.snake.body
    def update_snake_representation(self):
        if self.snake is not self.game.snake:
            self.snake = self.game.snake
            self.snake_representation = []

        for i in range(len(self.snake_representation), len(self.snake.body)):
            snake_x, snake_y = self.snake.body[i]

            self.snake_representation.append(pygame.Rect(snake_x, snake_y, cfg.SNAKE_SIZE, cfg.SNAKE_SIZE))
    
    def update_snake_position(self):
        for i in range(len(self.snake_representation)):
            snake_x, snake_y = self.snake.body[i]
            self.snake_representation[i].x = snake_x
            self.snake_representation[i].y = snake_y
    
    def update_food_position(self):
        food_x, food_y = self.game.food

        self.food.x = food_x
        self.food.y = food_y
    

    def draw(self):
        self.update_snake_representation()
        self.update_snake_position()
        self.update_food_position()
        
        self.screen.fill(self.black)

        # Draw game window
        pygame.draw.rect(self.screen, self.grey, self.game_window)

        self.draw_menu()

        self.draw_snake()
        self.draw_food()

    def draw_snake(self):
        # Draw head
        pygame.draw.rect(self.screen, self.red, self.snake_representation[0])

        # Draw body
        for i in range(1, len(self.snake_representation) - 1):
            pygame.draw.rect(self.screen, self.white, self.snake_representation[i])

        # Draw tail
        pygame.draw.rect(self.screen, self.black, self.snake_representation[-1])

    def draw_food(self):
        pygame.draw.rect(self.screen, self.green, self.food)

    def cycle_fps_setting(self):
        match self.display_setting:
            case None:
                self.display_setting = 0
            case 0:
                self.display_setting = 20
            case 20:
                self.display_setting = None


    def draw_menu(self):
        # Draw menu window
        pygame.draw.rect(self.screen, self.black, self.menu_window)

        # Draw score
        text_surface = self.score_font.render(f"Score: {self.game.score}", True, self.white)
        text_rect = text_surface.get_rect(center=(cfg.MENU_START_X + cfg.MENU_WINDOW_WIDTH // 2, 40))
        self.screen.blit(text_surface, text_rect)

        # Draw highscore
        text_surface = self.score_font.render(f"Highscore: {self.game.high_score}", True, self.white)
        text_rect = text_surface.get_rect(center=(cfg.MENU_START_X + cfg.MENU_WINDOW_WIDTH // 2, 60))
        self.screen.blit(text_surface, text_rect)

        # Display information about RL Agent
        if self.agent is not None:

            # Show average score
            text_surface = self.score_font.render(f"Average score: {self.game.average_score:.2f}", True, self.white)
            text_rect = text_surface.get_rect(center=(cfg.MENU_START_X + cfg.MENU_WINDOW_WIDTH // 2, 80))
            self.screen.blit(text_surface, text_rect)

            # Show epsilon number
            text_surface = self.score_font.render(f"Epsilon: {self.agent.epsilon:.2f}", True, self.white)
            text_rect = text_surface.get_rect(center=(cfg.MENU_START_X + cfg.MENU_WINDOW_WIDTH // 2, 120))
            self.screen.blit(text_surface, text_rect)

            # Show generation number
            text_surface = self.score_font.render(f"Generation: {self.agent.generation:,}", True, self.white)
            text_rect = text_surface.get_rect(center=(cfg.MENU_START_X + cfg.MENU_WINDOW_WIDTH // 2, 140))
            self.screen.blit(text_surface, text_rect)

            # Show steps number
            text_surface = self.score_font.render(f"Steps: {self.agent.steps:,}", True, self.white)
            text_rect = text_surface.get_rect(center=(cfg.MENU_START_X + cfg.MENU_WINDOW_WIDTH // 2, 160))
            self.screen.blit(text_surface, text_rect)


    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.game.done:
                self.game.reset_game()

            if event.key == pygame.K_SPACE:
                self.cycle_fps_setting()
            elif event.key == pygame.K_w or event.key == pygame.K_UP:
                self.snake.add_input("up")
            elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                self.snake.add_input("down")
            elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                self.snake.add_input("right")
            elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                self.snake.add_input("left")