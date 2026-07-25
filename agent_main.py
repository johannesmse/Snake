import pygame
import config as cfg
from ui import UI
from game import Game
from agent import Agent

pygame.init()
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()
screen = pygame.display.set_mode((cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT))
game = Game()
agent = Agent(game)
game_ui = UI(screen, game, agent)

game_ui.draw()
pygame.display.flip()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            game_ui.handle_event(event)
    
    if game.done:
        game.reset_game()
        agent.update_snake()
    else:
        agent.step()
    
    if game_ui.display_setting is not None:
        game_ui.draw()
        
        if game_ui.display_setting > 0:
            clock.tick(game_ui.display_setting)
    else:
        game_ui.draw_menu()

    pygame.display.flip()


pygame.quit()