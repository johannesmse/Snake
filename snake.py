import config as cfg

class Snake:
    def __init__(self, start_x, start_y, direction):
        self.direction = direction
        self.body = [[start_x, start_y]]
        self.initialize_body_parts(4)
        self.add_body_queue = 0
        self.input_queue = []
        self.max_input_queue = 2

    @property
    def head(self):
        return self.body[0]

    @property
    def tail(self):
        return self.body[-1]
    
    # Initializes the snake body when spawning
    def initialize_body_parts(self, n):
        for _ in range(n):
            last_element_x, last_element_y = self.body[-1]

            match self.direction:
                case "right":
                    self.body.append([last_element_x - cfg.SNAKE_SIZE, last_element_y])
                case "left":
                    self.body.append([last_element_x + cfg.SNAKE_SIZE, last_element_y])
                case "up":
                    self.body.append([last_element_x, last_element_y + cfg.SNAKE_SIZE])
                case "down":
                    self.body.append([last_element_x, last_element_y - cfg.SNAKE_SIZE])
    
    def add_body_parts(self, n):
        self.add_body_queue += n

    def add_input(self, command):
        if len(self.input_queue) > 0:
            if len(self.input_queue) == self.max_input_queue or self.input_queue[-1] == command:
                return

        self.input_queue.append(command)

    def change_direction(self, direction):
        if direction in cfg.VALID_TURNS[self.direction]:
            self.direction = direction
            return True
        
        return False
    
    def inside_itself(self):
        for i in range(1, len(self.body)):
            if self.head == self.body[i]:
                return True
            
        return False
    
    def move_body(self):
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i][0] = self.body[i - 1][0]
            self.body[i][1] = self.body[i - 1][1]

    def move_head(self):
        match self.direction:
            case "right":
                self.head[0]+= cfg.SNAKE_SIZE
            case "left":
                self.head[0]-= cfg.SNAKE_SIZE
            case "up":
                self.head[1]-= cfg.SNAKE_SIZE
            case "down":
                self.head[1]+= cfg.SNAKE_SIZE

    def move(self):
        if len(self.input_queue) > 0:
            self.change_direction(self.input_queue.pop(0))

        # Check if snake should grow
        if self.add_body_queue > 0:
            # Duplicate head and prepend
            new_head = [self.head[0], self.head[1]]
            self.body.insert(0, new_head)
            self.add_body_queue -= 1
        else:
            self.move_body()
            
        self.move_head()
        
