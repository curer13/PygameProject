import pygame as pg
import math
import random
import sys

#Sounds
pg.init()
pacman_begin = pg.mixer.Sound('pacman_beginning.wav')
pacman_death = pg.mixer.Sound('pacman_death.wav')
pacman_eatfruit = pg.mixer.Sound('pacman_eatfruit.wav')
pacman_eatghost = pg.mixer.Sound('pacman_eatghost.wav')
pacman_extrapac = pg.mixer.Sound('pacman_extrapac.wav')
pacman_intermission = pg.mixer.Sound('pacman_intermission.wav')
#pacman_ringtone = pg.mixer.Sound('pacman_ringtone.wav')
#pacman_ringtone_interlude = pg.mixer.Sound('pacman_ringtone_interlude.wav')

#Png
ball = pg.image.load('ball.png')
bigball = pg.image.load('bigball.png')
ghost = pg.image.load('ghost.png')
pacman_open_up = pg.image.load('pacman_open.png')
pacman_open_down = pg.transform.flip(pacman_open_up, True, False)
pacman_open_right = pg.transform.flip(pacman_open_up, True, True)
pacman_open_left = pg.transform.flip(pacman_open_up, False, False)
pacman_right = pg.image.load('pacman_right.png')
pacman_down = pg.transform.flip(pacman_right, True, False)
pacman_right_up = pg.transform.flip(pacman_right, True, True)
pacman_left = pg.transform.flip(pacman_right, False, False)



class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __str__(self):
        return f'Vector<{self.x}, {self.y}>'

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def asTuple(self):
        return self.x, self.y

    def __hash__(self):
        return id(self)

    def copy(self):
        return Vector(self.x, self.y)

    def normL2(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y:
            return True
        return False

    def asInt(self):
        return int(self.x), int(self.y)



# Directions
UP = Vector(0, -1)
DOWN = Vector(0, 1)
LEFT = Vector(-1, 0)
RIGHT = Vector(1, 0)
STOP = Vector(0, 0)
OPPOSITE_DIRECTIONS = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
PINK = (255, 192, 203)
BLUE = (0, 0, 255)
AMBER = (255, 191, 0)
left = False
right = False
walkCount = 0
# Another constants
BOTSIZE = (10, 10)
animation_increment=10
clock_tick_rate=20

class Creature:
    creatureList = []
    speed = 60

    def __init__(self, gridsystem):
        self.node = gridsystem.nodeList[-3]
        self.position = self.node.position.copy()
        self.direction = STOP
        self.target = None
        self.radius = 10
        self.color = YELLOW
        self.clock = pg.time.Clock()

    def set_target(self):
        if self.direction != STOP:
            self.target = self.node.neighbours[self.direction]
        else:
            self.target = None

    def set_position(self):
        self.position = self.node.position.copy()

    @staticmethod
    def get_valid_directions(node):
        directions = []
        neighbours = node.neighbours
        for direction in neighbours.keys():
            if neighbours[direction] is not None:
                directions.append(direction)
        return directions

    def get_valid_targets(self):
        targets = []
        directions = self.get_valid_directions(self.node)
        for direction in directions:
            targets.append(self.node.neighbours[direction])
        return targets

    def target_reached(self):
        if self.target is not None:
            if (self.node.position - self.position).normL2() + (self.position - self.target.position).normL2() > \
                    (self.node.position - self.target.position).normL2():
                return True
            return False
        return True

    def render(self, screen):
        pg.draw.circle(screen, self.color, self.position.asInt(), self.radius)

    def create(self):
        Creature.creatureList.append(self)

    def __eq__(self, other):
        return self.name == other.name


class Pacman(Creature):
    pg.mixer.music.load('pacman_chomp.wav')
    pg.mixer.music.play(-1)
    name = 'pacman'
    def __init__(self, gridsystem):
        Creature.__init__(self, gridsystem)
        self.init_node = gridsystem.nodeList[-3]
        self.node = self.init_node
        self.position = self.node.position.copy()
        self.lives = 3
        # self.speed = 60
        self.direction = STOP
        self.next_direction = STOP
        self.score = 0
        self.target = None
        self.radius = 10

    def move(self):
        dt = self.clock.tick(30) / 1000
        neighbours = self.node.neighbours
        #walkRight=[pg.image.load('pacman_open.png'),pg.image.load('pacman_right.png')]
        #walkLeft=[pg.image.load('pacman_open.png'),pg.image.load('pacman_right.png')]
        #walkUp=[pg.image.load('pacman_open.png'),pg.image.load('pacman_right.png')]
        #walkDown=[pg.image.load('pacman_open.png'),pg.image.load('pacman_right.png')]
        #keys = pygame.key.get_pressed()
        #if left:  
        #    win.blit(walkLeft[walkCount//3], (x,y))
        #    walkCount += 1                          
        #elif right:
        #    win.blit(walkRight[walkCount//3], (x,y))
        #    walkCount += 1
        #elif up:
        #   win.blit(walkUp[walkCount//3], (x,y))
        #    walkCount += 1
        #elif down:
        #    win.blit(walkDown[walkCount//3], (x,y))
        #    walkCount += 1
        #else:
        #    win.blit(char, (x, y))
        #   walkCount = 0
        if neighbours[self.direction] is not None:
            self.position += self.direction * Creature.speed * dt
            if self.target_reached():
                if self.next_direction != STOP:
                    self.direction = self.next_direction
                self.node = self.target
                self.set_position()
                if self.node.type == 'portal':
                    self.node = self.node.pair
                    self.set_position()
            else:
                self.move_reverse()

    def move_reverse(self):
        if self.next_direction.asTuple() == (self.direction * (-1)).asTuple():
            self.direction = self.next_direction
            cash = self.node
            self.node = self.target
            self.target = cash

    def set_direction(self, key):
        if self.target_reached():
            self.next_direction = STOP
            new_direction = self.find_key_direction(self.node, key)
            if new_direction:
                self.direction = new_direction
        else:
            new_direction = self.find_key_direction(self.target, key)
            if new_direction:
                self.next_direction = new_direction

    def find_key_direction(self, node, key):
        key_dict = {
            (pg.K_UP, UP): UP,
            (pg.K_DOWN, DOWN): DOWN,
            (pg.K_LEFT, LEFT): LEFT,
            (pg.K_RIGHT, RIGHT): RIGHT
        }
        directions = self.get_valid_directions(node)
        for direction in directions:
            if (key, direction) in key_dict.keys():
                return key_dict[(key, direction)]
        return None

    def check_food(self, food):
        if food.position is not None:
            if self.collide_food(food):
                self.eat(food)
    

    def collide_food(self, food):
        distance = (self.position - food.position).normL2()
        if distance <= food.radius:
            return True
        return False

    def eat(self, food):
        if food.name == 'Pellet':
            if food.type == 'small':
                self.score += 10
            elif food.type == 'big':
                for creature in Creature.creatureList:
                    if creature != self:
                        creature.mode = 'frighten'
                self.score += 50
        elif food.name == 'fruit':
            self.life += 1
        food.disappear()

    def alive(self):
        if self.lives <= 0:
            return False
        return True

    def collide_ghost(self):
        for creature in Creature.creatureList:
            if creature != self:
                distance = (creature.position - self.position).normL2()
                if 1.5 * self.radius >= distance >= 0:
                    return True
        return False

    def check_ghosts(self):
        
        if self.collide_ghost():
            pg.mixer.Sound.play(pacman_death)
            pg.mixer.music.pause()
            pg.mixer.music.unpause()
            self.lives -= 1
            self.node = self.init_node
            self.position = self.node.position.copy()


class Node:

    def __init__(self, grid_x, grid_y):
        self.g_x = grid_x
        self.g_y = grid_y
        self.position = Vector(grid_x * BOTSIZE[0], grid_y * BOTSIZE[1])
        self.neighbours = {UP: None, DOWN: None, LEFT: None, RIGHT: None, STOP: None}
        self.type = 'regular'
        self.pair = None

    def __str__(self):
        return f'<Node({self.g_x},{self.g_y})>'

    def set_neighbour(self, neighbour, direction):
        self.neighbours[direction] = neighbour

    def render(self, screen):
        pg.draw.circle(screen, RED, self.position.asTuple(), 5)
        neighbours = self.neighbours
        for direction in neighbours.keys():
            if neighbours[direction]:
                pg.draw.line(screen, WHITE, self.position.asTuple(),
                             neighbours[direction].position.asTuple(), 2)

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        if self.g_x == other.g_x and self.g_y == other.g_y:
            return True
        return False


class NodeGroup:

    def __init__(self):
        self.nodeList = []

    def __str__(self):
        return f'{[node.__str__() for node in self.nodeList]}'

    def createGroup(self):
        with open('maze1.txt', 'r') as file:
            maze = file.readlines()
            portal_list = []
            for i in range(len(maze)):
                for j in range(len(maze[i])):
                    if maze[i][j] == '+' or maze[i][j] == '1':
                        node = Node(j, i * 2)
                        self.nodeList.append(node)
                    if maze[i][j] == '1':
                        node.type = 'portal'
                        portal_list.append(node)

            portal_list[0].pair = portal_list[1]
            portal_list[1].pair = portal_list[0]

            for node in self.nodeList:
                g_x = node.g_x
                g_y = node.g_y
                i = g_y // 2
                j = g_x
                if (i + 1) < len(maze) and (j + 2) < len(maze[i]):
                    if maze[i][j + 2] == '-':
                        ind = maze[i].find('+', j + 1)
                        if ind == -1:
                            ind = maze[i].find('1', j + 1)
                        if ind != -1:
                            neighbour_r = Node(ind, i * 2)
                            i_elem = self.nodeList.index(neighbour_r)
                            node.set_neighbour(self.nodeList[i_elem], RIGHT)
                            self.nodeList[i_elem].set_neighbour(node, LEFT)
                    if maze[i + 1][j] == '|':
                        string = ''
                        for k in range(len(maze)):
                            string += maze[k][j]
                        ind = string.find('+', i + 1)
                        if ind == -1:
                            ind = string.find('1', i + 1)
                        if ind != -1:
                            neighbour_d = Node(j, ind * 2)
                            i_elem = self.nodeList.index(neighbour_d)
                            node.set_neighbour(self.nodeList[i_elem], DOWN)
                            self.nodeList[i_elem].set_neighbour(node, UP)

    def render(self, screen):
        for node in self.nodeList:
            node.render(screen)


class Pellet:
    name = 'Pellet'

    def __init__(self, type_, g_x, g_y):
        self.type = type_
        self.g_x = g_x
        self.g_y = g_y
        self.radius = (4, 7)[self.type == 'big']
        self.position = Vector(g_x * BOTSIZE[0], g_y * BOTSIZE[1])

    def render(self, screen):
        if self.position is not None:
            pg.draw.circle(screen, YELLOW, self.position.asInt(), self.radius)
        

    def disappear(self):
        self.position = None

    def __hash__(self):
        return id(self)


class PelletGroup:
    def __init__(self):
        self.pelletList = []

    def createGroup(self):
        with open('pellets.txt', 'r') as file:
            maze = file.readlines()
            for i in range(len(maze)):
                for j in range(len(maze[i])):
                    if maze[i][j] == 'p':
                        self.pelletList.append(Pellet('small', j, i * 2))
                    elif maze[i][j] == 'P':
                        self.pelletList.append(Pellet('big', j, i * 2))

    def render(self, screen):
        for pellet in self.pelletList:
            pellet.render(screen.blit(ball))


class Ghost(Creature):
    name = 'ghost'
    random.seed(42)

    def __init__(self, gridsystem, color, node_elem):
        Creature.__init__(self, gridsystem)
        self.color = color
        self.init_node = gridsystem.nodeList[node_elem]
        self.node = self.init_node
        self.position = self.node.position.copy()
        self.goal = gridsystem.nodeList[-3].position
        self.mode = 'regular'
        self.speed = Creature.speed

    def set_best_direction(self):
        self.direction = self.best_direction(self.get_valid_directions(self.node))

    def set_random_direction(self):
        directions = self.get_valid_directions(self.node)
        r = random.randint(0, len(directions)-1)
        self.direction = directions[r]

    def best_direction(self, valid_directions):
        distances = []
        for direction in valid_directions:
            distance = self.node.position + direction * BOTSIZE[0] - self.goal
            distances.append(distance.normL2())
        i = distances.index(min(distances))
        return valid_directions[i]

    def set_goal(self, pacman):
        # if self.goal_reached():
        if pacman.direction is not STOP:
            noise = (pacman.direction, OPPOSITE_DIRECTIONS[pacman.direction])[random.randint(0, 1)]
            self.goal = pacman.position.copy() + noise*BOTSIZE[0]

    def goal_reached(self):
        if (self.position - self.goal).normL2() <= self.radius:
            return True
        return False

    def check_mode(self):
        if self.mode == 'frighten':
            self.speed = Creature.speed / 1.5

    def move(self):
        self.check_mode()
        dt = self.clock.tick(30) / 1000
        if self.target_reached():
            if self.target is not None:
                self.node = self.target
            if self.node.type == 'portal':
                self.node = self.node.pair
            self.set_position()
            r = random.randint(0, 1)
            if r:
                self.set_random_direction()
            else:
                self.set_best_direction()
            self.set_target()

        self.position += self.direction * self.speed * dt
    

def main():
    pg.init()
    EXIT = False

    # Initializing the screen
    SIZE = (540, 1000)
    screen = pg.display.set_mode(SIZE)

    # Creating the Grid of Nodes
    nodes = NodeGroup()
    nodes.createGroup()

    # Creating pellets
    pellets = PelletGroup()
    pellets.createGroup()

    # Creating The Pacman
    pacman = Pacman(nodes)
    pacman.create()

    # Creating a ghost
    pinky = Ghost(nodes, PINK, 10)
    pinky.create()
    inky = Ghost(nodes, BLUE, 15)
    inky.create()
    clyde = Ghost(nodes, AMBER, 20)
    clyde.create()
    blinky = Ghost(nodes, RED, 25)
    blinky.create()

    while not EXIT:
        if not pacman.alive():
            EXIT = True
        #clock = pg.time.Clock()
        #bg = pg.image.load('background.png').convert()
        #screen.blit(bg,[0,0])
        #pg.display.flip()
        #clock.tick(clock_tick_rate)
        screen.fill(BLACK)
        nodes.render(screen)
        pellets.render(screen)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                EXIT = True
            if event.type == pg.KEYDOWN:
                pacman.set_direction(event.key)

        pinky.set_goal(pacman)
        pinky.move()
        inky.set_goal(pacman)
        inky.move()
        clyde.set_goal(pacman)
        clyde.move()
        blinky.set_goal(pacman)
        blinky.move()
        pacman.set_target()
        pacman.move()

        for food in pellets.pelletList:
            pacman.check_food(food)
        pacman.check_ghosts()

        pacman.render(screen)
        pinky.render(screen)
        inky.render(screen)
        clyde.render(screen)
        blinky.render(screen)
        pg.display.flip()

    pg.quit()


while True:
    more =int(input())
    if more:
        main()
    else:
        break
