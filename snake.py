import config as cfg

class Snake:
    def __init__(self):
        self.direction = "right"
        self.body = [[400, 400]]
        self.add_body_parts(4)

    def add_body_parts(self, n):

        for _ in range(n):
            last_element_x = self.body[-1][0]
            last_element_y = self.body[-1][1]

            match self.direction:
                case "right":
                    self.body.append([last_element_x - cfg.SNAKE_SIZE, last_element_y])
                case "left":
                    self.body.append([last_element_x + cfg.SNAKE_SIZE, last_element_y])
                case "up":
                    self.body.append([last_element_x, last_element_y + cfg.SNAKE_SIZE])
                case "down":
                    self.body.append([last_element_x, last_element_y - cfg.SNAKE_SIZE])

    def change_direction(self, direction):
        if direction in cfg.VALID_TURNS[self.direction]:
            self.direction = direction
            return True
        
        return False
    
    def move(self):
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i][0] = self.body[i - 1][0]
            self.body[i][1] = self.body[i - 1][1]

        match self.direction:
                case "right":
                    self.body[0][0]+= cfg.SNAKE_SIZE
                case "left":
                    self.body[0][0]-= cfg.SNAKE_SIZE
                case "up":
                    self.body[0][1]-= cfg.SNAKE_SIZE
                case "down":
                    self.body[0][1]+= cfg.SNAKE_SIZE
        

