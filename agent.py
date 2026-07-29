import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import config as cfg
from game import Game
from snake import Snake
import torch
import torch.nn as nn
import random
import copy
from collections import deque

class SnakeNet(nn.Module):
    def __init__(self, input_size, output_size):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(input_size, 256), # Hidden layer 1
            nn.ReLU(),

            nn.Linear(256, 128), # Hidden layer 2
            nn.ReLU(),

            nn.Linear(128, output_size) # Output layer
        )
    
    def forward(self, x):
        return self.network(x)


class Agent:
    def __init__(self, game):
        self.game = game
        self.snake = self.game.snake
        self.rows = int(cfg.GAME_WINDOW_HEIGHT / cfg.SNAKE_SIZE)
        self.columns = int(cfg.GAME_WINDOW_WIDTH / cfg.SNAKE_SIZE)
        self.output_size = 3

        self.discount_factor = 0.99
        self.learning_rate = 0.0003
        self.epsilon = 1
        self.epsilon_decay = 0.99998
        self.epsilon_min = 0

        self.replay_buffer = deque(maxlen=50_000)
        self.replay_batch_size = 64
        self.training_freq = 4

        self.generation = 0
        self.steps = 0

        self.number_of_input_channels = 4
        self.input_size = 4 + (self.rows * self.columns * self.number_of_input_channels)

        self.model = SnakeNet(self.input_size, self.output_size)
        self.target_model = copy.deepcopy(self.model)

        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.loss_function = nn.MSELoss()


        self.action_map = {
            "up" : ["left", "right"],
            "down" : ["right", "left"],
            "left" : ["down", "up"],
            "right" : ["up", "down"]
        }

        # Used to encode game state
        self.direction_encoding = {
            "right" : [1, 0, 0, 0],
            "left" : [0, 1, 0, 0],
            "up" : [0, 0, 1, 0],
            "down" : [0, 0, 0, 1]
        }
    def update_snake(self):
        self.snake = self.game.snake

    def get_current_state(self):
        direction = self.direction_encoding[self.snake.direction]
        head_channel = [0] * self.rows * self.columns
        body_channel = [0] * self.rows * self.columns
        tail_channel = [0] * self.rows * self.columns
        food_channel = [0] * self.rows * self.columns

        # Add head
        x, y = self.snake.head
        head_channel[self.convert_to_grid_number(x, y)] = 1

        # Add body
        for i in range(1, len(self.snake.body) - 1):
            x, y = self.snake.body[i]
            body_channel[self.convert_to_grid_number(x, y)] = 1

        # Add tail
        x, y = self.snake.tail
        tail_channel[self.convert_to_grid_number(x, y)] = 1

        # Add food
        x, y = self.game.food
        food_channel[self.convert_to_grid_number(x, y)] = 1

        return direction + head_channel + body_channel + tail_channel + food_channel
    
    def get_action_epsilon_greedy(self, state):
        if random.random() > self.epsilon:
            # Return optimal action
            state = torch.tensor(state, dtype=torch.float32)
            q_values = self.model(state)

            return torch.argmax(q_values).item()
        else:
            # Return random action
            return random.randrange(3)

    def get_action_optimal(self, state):
        state = torch.tensor(state, dtype=torch.float32)
        q_values = self.model(state)

        return torch.argmax(q_values).item()


    def perform_action(self, action):
        """
        Action 0 and 1 from model is transformed to correct action using self.action_map
        Action 2 represents going straight 
        """

        if action != 2:
            snake_action = self.action_map[self.snake.direction][action]
            self.snake.add_input(snake_action)

    def step(self):
        self.steps += 1

        # Get current state
        state = self.get_current_state()

        # Choose and perform action
        action = self.get_action_epsilon_greedy(state)
        self.perform_action(action)

        # Advance game one step
        self.game.update_game()

        # Get reward and check if game is over
        reward = self.game.reward
        done = self.game.done

        # Get new state if game is not over
        if done:
            next_state = None
            self.generation += 1
        else:
            next_state = self.get_current_state()

        # Add experience to replay buffer
        self.replay_buffer.append((state, action, reward, next_state))

        if self.steps % self.training_freq == 0:
            self.train()

        # Update epsilon to reduce exploration
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

        # Update target network every 2000 steps
        if self.steps % 2000 == 0:
            self.target_model.load_state_dict(self.model.state_dict())

        # Print scores in terminal
        if self.steps % 100000 == 0:
            print(f"Steps: {self.steps:,}")
            self.game.print_scores()
        

    
    def train(self):
        """
        Experience replay batch training with Double DQN
        Does two forward passes for online network (current and next states) and one for the target network(next states),
        one backward pass and one Adam update per train() call with buffer of batch_size.

        Compared to old train method that did batch_size number of forward passes, backward passes
        and weight updates.
        """

        if len(self.replay_buffer) < self.replay_batch_size:
            return

        # Sample replay batch
        batch = random.sample(self.replay_buffer, self.replay_batch_size)
        states, actions, rewards, next_states = zip(*batch)
        
        # Remove None elements from next_states
        filtered_next_states = [next_state for next_state in next_states if next_state is not None]

        states = torch.tensor(states, dtype=torch.float32)
        filtered_next_states = torch.tensor(filtered_next_states, dtype=torch.float32)

        # Current state q_values from online network
        q_values = self.model(states)
        target_q_values = q_values.clone().detach()

        # Gets q_values for next state from both models to implement Double DQN
        with torch.no_grad():
            next_states_target_q_values = self.target_model(filtered_next_states)
            next_states_online_q_values = self.model(filtered_next_states)

        filtered_next_states_index = 0
        for i, (action, reward, next_state) in enumerate(zip(actions, rewards, next_states)):
            if next_state is None:
                target = reward
            else:
                next_state_max_action = torch.argmax(next_states_online_q_values[filtered_next_states_index]).item()
                target = reward + self.discount_factor * next_states_target_q_values[filtered_next_states_index][next_state_max_action].item()
                filtered_next_states_index += 1

            target_q_values[i][action] = target

        # Clear old gradients
        self.optimizer.zero_grad()

        # Calculate loss and update model
        loss = self.loss_function(q_values, target_q_values)
        loss.backward()
        self.optimizer.step()


    # Old train function
    def train_old(self):
        # Sample replay batch
        batch = random.sample(self.replay_buffer, self.replay_batch_size)

        for state, action, reward, next_state in batch:
            state = torch.tensor(state, dtype=torch.float32)
            q_values = self.model(state)

            # Next state is terminal state and target is the reward
            if next_state is None:
                target = reward
            else:
                next_state = torch.tensor(next_state, dtype=torch.float32)

                # Get next state q-values from target network without autograd relationship
                with torch.no_grad():
                    next_state_q_values = self.target_model(next_state)
                    target = reward + self.discount_factor * torch.max(next_state_q_values).item()

            # Replace q_value of action taken with target q_value
            target_q_values = q_values.clone().detach()
            target_q_values[action] = target

            # Clear old gradients
            self.optimizer.zero_grad()

            # Calculate loss and update model
            loss = self.loss_function(q_values, target_q_values)
            loss.backward()
            self.optimizer.step()


    
    def convert_action(self, action):
        return self.action_map[self.snake.direction][action]

    def convert_to_grid_number(self, x, y):
        grid_x = int(x / cfg.SNAKE_SIZE)
        grid_y = int(y / cfg.SNAKE_SIZE)

        return grid_y * self.columns + grid_x
    
    def print_state(self, state):
        print("\nDirection:", state[:4])

        board = state[4:]

        channel_size = self.rows * self.columns

        head_channel = board[:channel_size]
        body_channel = board[channel_size:2 * channel_size]
        tail_channel = board[2 * channel_size:3 * channel_size]
        food_channel = board[3 * channel_size:]

        channels = [
            ("Head", head_channel),
            ("Body", body_channel),
            ("Tail", tail_channel),
            ("Food", food_channel)
        ]

        for name, channel in channels:
            print(f"\n{name} channel:")

            for row in range(self.rows):
                start = row * self.columns
                end = start + self.columns

                print(" ".join(str(cell) for cell in channel[start:end]))