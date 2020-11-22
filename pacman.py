import pygame as pg
import math


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __str__(self):
        return f'<{self.x}, {self.y}>'

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def asTuple(self):
        return self.x, self.y

    def __hash__(self):
        return id(Vector)

    def copy(self):
        return Vector(self.x, self.y)

    def normL2(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)


# Directions
UP = Vector(0, -1)
DOWN = Vector(0, 1)
LEFT = Vector(-1, 0)
RIGHT = Vector(1, 0)
STOP = Vector(0, 0)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

# Another constants
BOTSIZE = (10, 10)


class Pacman:

    def __init__(self, gridsystem):
        self.name = 'pacman'
        self.x = 100
        self.y = 100
        self.node = gridsystem.nodeList[0]
        self.position = self.node.position.copy()
        self.lives = 3
        self.speed = 60
        self.direction = STOP
        self.next_direction = STOP
        self.score = 0
        self.target = None

    def move(self):
        dt = pg.time.Clock().tick(30) / 1000
        neighbours = self.node.neighbours
        if self.direction != STOP and neighbours[self.direction] is not None:
            self.position += self.direction * self.speed * dt
            if self.target_reached():
                if self.next_direction != STOP:
                    self.direction = self.next_direction
                self.node = self.target
                self.position = self.node.position.copy()
            else:
                if self.next_direction.asTuple() == (self.direction*(-1)).asTuple():
                    self.direction = self.next_direction
                    cash = self.node
                    self.node = self.target
                    self.target = cash
                # self.node = neighbours[self.direction]
                # self.position = neighbours[self.direction].position

    def set_direction(self, key):
        if self.target_reached():
            self.next_direction = STOP
            neighbours = self.node.neighbours
            for direction in neighbours:
                if neighbours[direction]:
                    if key == pg.K_UP and direction == UP:
                        self.direction = UP
                    elif key == pg.K_DOWN and direction == DOWN:
                        self.direction = DOWN
                    elif key == pg.K_LEFT and direction == LEFT:
                        self.direction = LEFT
                    elif key == pg.K_RIGHT and direction == RIGHT:
                        self.direction = RIGHT
        else:
            neighbours = self.target.neighbours
            for direction in neighbours:
                if neighbours[direction]:
                    if key == pg.K_UP and direction == UP:
                        self.next_direction = UP
                    elif key == pg.K_DOWN and direction == DOWN:
                        self.next_direction = DOWN
                    elif key == pg.K_LEFT and direction == LEFT:
                        self.next_direction = LEFT
                    elif key == pg.K_RIGHT and direction == RIGHT:
                        self.next_direction = RIGHT
        '''key_dict = {
                    (pg.K_UP, UP): UP,
                    (pg.K_DOWN, DOWN): DOWN,
                    (pg.K_LEFT, LEFT): LEFT,
                    (pg.K_RIGHT, RIGHT): RIGHT
                }
        for direction in neighbours.keys():
            if (key, direction) in key_dict.keys():
                self.direction = key_dict[(key, direction)]'''

    def target_reached(self):
        if self.target is not None:
            if (self.node.position - self.position).normL2() + (self.position - self.target.position).normL2() > \
                    (self.node.position - self.target.position).normL2():
                return True
            return False
        return True

    def set_target(self):
        if self.direction != STOP:
            neighbour = self.node.neighbours[self.direction]
            if neighbour is not None:
                self.target = neighbour
            else:
                self.target = None
        return None

    def eat(self, food):
        if food == 'frighten_ghost':
            self.score += 200
        elif food == 'small_dot':
            self.score += 10
        elif food == 'big_dot':
            ghost.type = 'frighten_ghost'
        elif food == 'fruit':
            self.life += 1

    def alive(self):
        if self.lives <= 0:
            return False
        return True

    def render(self, screen):
        pg.draw.circle(screen, YELLOW, self.position.asTuple(), 10)


class Node:

    def __init__(self, grid_x, grid_y):
        self.position = Vector(grid_x * BOTSIZE[0], grid_y * BOTSIZE[1])
        self.neighbours = {UP: None, DOWN: None, LEFT: None, RIGHT: None}

    def set_neighbour(self, neighbour, direction):
        self.neighbours[direction] = neighbour

    def render(self, screen):
        pg.draw.circle(screen, RED, self.position.asTuple(), 5)
        neighbours = self.neighbours
        for direction in neighbours.keys():
            if neighbours[direction]:
                pg.draw.line(screen, WHITE, self.position.asTuple(),
                             neighbours[direction].position.asTuple(), 2)


class NodeGroup:

    def __init__(self):
        self.nodeList = []

    def createGroup(self, *nodes):
        for node in nodes:
            self.nodeList.append(node)

    def render(self, screen):
        for node in self.nodeList:
            node.render(screen)


def main():
    pg.init()
    game_over = False

    # Initializing the screen
    SIZE = (500, 500)
    screen = pg.display.set_mode(SIZE)
    # background = pg.Surface(SIZE)
    # screen.blit(background, (0, 0))

    # Creating the Grid of Nodes
    node1 = Node(3, 3)
    node2 = Node(13, 3)
    node3 = Node(23, 3)
    node4 = Node(3, 13)
    node5 = Node(13, 13)
    node6 = Node(23, 13)
    node7 = Node(13, 23)
    node8 = Node(23, 23)
    node1.set_neighbour(node2, RIGHT)
    node1.set_neighbour(node4, DOWN)
    node2.set_neighbour(node1, LEFT)
    node2.set_neighbour(node3, RIGHT)
    node3.set_neighbour(node2, LEFT)
    node3.set_neighbour(node6, DOWN)
    node4.set_neighbour(node1, UP)
    node4.set_neighbour(node5, RIGHT)
    node5.set_neighbour(node4, LEFT)
    node5.set_neighbour(node6, RIGHT)
    node5.set_neighbour(node7, DOWN)
    node6.set_neighbour(node3, UP)
    node6.set_neighbour(node5, LEFT)
    node6.set_neighbour(node8, DOWN)
    node7.set_neighbour(node5, UP)
    node7.set_neighbour(node8, RIGHT)
    node8.set_neighbour(node6, UP)
    node8.set_neighbour(node7, LEFT)
    nodes = NodeGroup()
    nodes.createGroup(node1, node2, node3, node4, node5, node6, node7, node8)

    # Creating The Pacman
    pacman = Pacman(nodes)
    # print(pacman.direction)
    # pacman.position = Vector(45.943, 30)
    # pacman.direction = RIGHT
    print(UP.asTuple() == (DOWN*(-1)).asTuple())

    while not game_over:
        screen.fill(BLACK)
        nodes.render(screen)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_over = True
            if event.type == pg.KEYDOWN:
                pacman.set_direction(event.key)

        pacman.set_target()
        pacman.move()
        pacman.render(screen)
        pg.display.flip()

    # print(pacman.direction)


main()
