import pygame
import config as cfg
from ui import UI
from game import Game
from agentff import AgentFF
from agentcnn import AgentCNN
import time

pygame.init()
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()
screen = pygame.display.set_mode((cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT))
game = Game()
agent_ff = AgentFF(game)
agent_cnn = AgentCNN(game)
game_ui = UI(screen, game, agent_cnn)

game_ui.draw()
pygame.display.flip()

last_menu_update = time.time()

running = True
while running:

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            game_ui.handle_event(event)

    # Train agent
    if game.done:
        game.reset_game()
        agent_cnn.update_snake()
    else:
        agent_cnn.step()

    # Display snake and menu
    if game_ui.display_setting is not None:
        game_ui.draw()
        pygame.display.flip()
        
        if game_ui.display_setting > 0:
            clock.tick(game_ui.display_setting)

    # Only display menu, update every 0.5 sec to reduce overhead
    elif time.time() - last_menu_update >= 0.5:
        game_ui.draw_menu()
        pygame.display.flip()
        last_menu_update = time.time()


pygame.quit()