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
        self.node = gridsystem.nodeList[-3]
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
                if self.node.type == 'portal':
                    self.node = self.node.pair
                    self.position = self.node.position.copy()
            else:
                if self.next_direction.asTuple() == (self.direction * (-1)).asTuple():
                    self.direction = self.next_direction
                    cash = self.node
                    self.node = self.target
                    self.target = cash


    def set_direction(self, key):
        if self.target_reached():
            self.next_direction = STOP
            new_direction = self.find_direction(self.node, key)
            if new_direction:
                self.direction = new_direction
        else:
            new_direction = self.find_direction(self.target, key)
            if new_direction:
                self.next_direction = new_direction

    @staticmethod
    def find_direction(node, key):
        key_dict = {
            (pg.K_UP, UP): UP,
            (pg.K_DOWN, DOWN): DOWN,
            (pg.K_LEFT, LEFT): LEFT,
            (pg.K_RIGHT, RIGHT): RIGHT
        }
        neighbours = node.neighbours
        for direction in neighbours.keys():
            if neighbours[direction]:
                if (key, direction) in key_dict.keys():
                    return key_dict[(key, direction)]

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
        self.g_x = grid_x
        self.g_y = grid_y
        self.position = Vector(grid_x * BOTSIZE[0], grid_y * BOTSIZE[1])
        self.neighbours = {UP: None, DOWN: None, LEFT: None, RIGHT: None}
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

    def createGroup(self):  # , *nodes):
        '''for node in nodes:
            self.nodeList.append(node)'''

        with open('maze1.txt', 'r') as file:
            maze = file.readlines()
            portal_list = []
            for i in range(len(maze)):
                for j in range(len(maze[i])):
                    if maze[i][j] == '+' or maze[i][j] == '1':
                        node = Node(j + 1, i + 1)
                        self.nodeList.append(node)
                    if maze[i][j] == '1':
                        node.type = 'portal'
                        portal_list.append(node)

            portal_list[0].pair = portal_list[1]
            portal_list[1].pair = portal_list[0]

            for node in self.nodeList:
                g_x = node.g_x
                g_y = node.g_y
                i = g_y - 1
                j = g_x - 1
                if (i + 1) < len(maze) and (j + 2) < len(maze[i]):
                    if maze[i][j + 2] == '-':
                        ind = maze[i].find('+', j + 1)
                        if ind == -1:
                            ind = maze[i].find('1', j + 1)
                        if ind != -1:
                            neighbour_r = Node(ind + 1, i + 1)
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
                            neighbour_d = Node(j + 1, ind + 1)
                            i_elem = self.nodeList.index(neighbour_d)
                            node.set_neighbour(self.nodeList[i_elem], DOWN)
                            self.nodeList[i_elem].set_neighbour(node, UP)

    def render(self, screen):
        for node in self.nodeList:
            node.render(screen)


def main():
    pg.init()
    game_over = False

    # Initializing the screen
    SIZE = (600, 500)
    screen = pg.display.set_mode(SIZE)
    # background = pg.Surface(SIZE)
    # screen.blit(background, (0, 0))

    # Creating the Grid of Nodes
    nodes = NodeGroup()
    nodes.createGroup()
    # print(node1)
    # print(Node(3, 3) not in nodes.nodeList)
    # print(Node(3, 2) in nodes.nodeList)
    print([i.type for i in nodes.nodeList])

    # Creating The Pacman
    pacman = Pacman(nodes)
    # print(pacman.direction)
    # pacman.position = Vector(45.943, 30)
    # pacman.direction = RIGHT
    # print(UP.asTuple() == (DOWN*(-1)).asTuple())

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
