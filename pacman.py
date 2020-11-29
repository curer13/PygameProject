import pygame as pg
import math
import random


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

# Another constants
BOTSIZE = (10, 10)


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
        self.gridsystem = gridsystem

    def set_target(self):
        if self.direction != STOP:
            self.target = self.node.neighbours[self.direction]
        else:
            self.target = None

    def set_position(self):
        self.position = self.node.position.copy()

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
        self.gridsystem = gridsystem

    def move(self):
        dt = self.clock.tick(30) / 1000
        neighbours = self.node.neighbours
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

    def set_target(self):
        if self.direction != STOP:
            self.target = self.node.neighbours[self.direction]
        else:
            self.target = None

    def get_valid_directions(self, node):
        directions = []
        neighbours = node.neighbours
        for direction in neighbours.keys():
            if neighbours[direction] is not None and\
                    neighbours[direction] not in self.gridsystem.ghost_nodeList:
                directions.append(direction)
        return directions

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
                    if creature != self and creature.mode != 'eaten':
                        creature.frighten()
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
                    return True, creature
        return False, None

    def check_ghosts(self):
        if self.collide_ghost()[0]:
            ghost = self.collide_ghost()[1]
            if ghost.mode == 'regular':
                self.lives -= 1
                self.node = self.init_node
                self.position = self.node.position.copy()
            elif ghost.mode == 'frighten':
                self.score += 200
                ghost.eaten()


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
        pg.draw.circle(screen, RED, self.position.asTuple(), 2)
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
        self.ghost_nodeList = []

    def __str__(self):
        return f'{[node.__str__() for node in self.nodeList]}'

    def createGroup(self):
        with open('maze1.txt', 'r') as file:
            maze = file.readlines()
            portal_list = []
            g_and_p = ['+', '1']
            g_only = ['P', 'I', 'B', 'C', 'a', 'b', 'H']
            # g_all = g_and_p+g_only
            for i in range(len(maze)):
                for j in range(len(maze[i])):
                    if maze[i][j] in g_and_p:
                        node = Node(j, i * 2)
                        self.nodeList.append(node)
                    if maze[i][j] == '1':
                        node.type = 'portal'
                        portal_list.append(node)
                    if maze[i][j] in g_only:
                        node = Node(j, i * 2)
                        self.ghost_nodeList.append(node)

            portal_list[0].pair = portal_list[1]
            portal_list[1].pair = portal_list[0]

            node = self.ghost_nodeList[3]
            g_x = node.g_x
            g_y = node.g_y
            i = g_y // 2
            j = g_x
            ind = i - 3
            neighbour_u = Node(j, ind * 2)
            n_i = self.nodeList.index(neighbour_u)
            node.set_neighbour(self.nodeList[n_i], UP)
            self.nodeList[n_i].set_neighbour(node, DOWN)

            self.ghost_nodeList[0].set_neighbour(self.ghost_nodeList[2], DOWN)
            self.ghost_nodeList[2].set_neighbour(self.ghost_nodeList[0], UP)
            self.ghost_nodeList[2].set_neighbour(self.ghost_nodeList[5], DOWN)
            self.ghost_nodeList[5].set_neighbour(self.ghost_nodeList[2], UP)
            self.ghost_nodeList[2].set_neighbour(self.ghost_nodeList[3], RIGHT)
            self.ghost_nodeList[3].set_neighbour(self.ghost_nodeList[2], LEFT)
            self.ghost_nodeList[3].set_neighbour(self.ghost_nodeList[4], RIGHT)
            self.ghost_nodeList[4].set_neighbour(self.ghost_nodeList[3], LEFT)
            self.ghost_nodeList[4].set_neighbour(self.ghost_nodeList[1], UP)
            self.ghost_nodeList[1].set_neighbour(self.ghost_nodeList[4], DOWN)
            self.ghost_nodeList[4].set_neighbour(self.ghost_nodeList[6], DOWN)
            self.ghost_nodeList[6].set_neighbour(self.ghost_nodeList[4], UP)

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
                    if maze[i][j+2] == '+':
                        neighbour_r = Node(j + 2, i * 2)
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
        for node in self.nodeList + self.ghost_nodeList:
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
            pellet.render(screen)

    def count(self):
        c = 0
        for pellet in self.pelletList:
            if pellet.position is not None:
                c += 1
        return c


class Ghost(Creature):
    name = 'ghost'
    random.seed(42)

    def __init__(self, gridsystem, color, node_elem):
        Creature.__init__(self, gridsystem)
        self.color = color
        self.init_node = gridsystem.ghost_nodeList[node_elem]
        self.node = self.init_node
        self.position = self.node.position.copy()
        self.goal = gridsystem.nodeList[-3].position.copy()
        self.mode = 'regular'
        self.speed = Creature.speed
        self.time = 0

    def set_best_direction(self):
        direction = self.best_direction(self.get_valid_directions(self.node), self.goal)
        if direction * (-1) != self.direction:
            self.direction = direction

    def set_random_direction(self):
        directions = self.get_valid_directions(self.node)
        r = random.randint(0, len(directions) - 1)
        self.direction = directions[r]

    def best_direction(self, valid_directions, goal):
        distances = []
        for direction in valid_directions:
            distance = self.node.position + direction * BOTSIZE[0] - goal
            distances.append(distance.normL2())
        i = distances.index(min(distances))
        return valid_directions[i]

    @staticmethod
    def get_valid_directions(node):
        directions = []
        neighbours = node.neighbours
        for direction in neighbours.keys():
            if neighbours[direction] is not None:
                directions.append(direction)
        return directions

    def set_direction(self):
        if self.mode == 'regular':
            r = random.randint(0, 1)
            if r:
                self.set_random_direction()
            else:
                self.set_best_direction()
        elif self.mode == 'frighten':
            self.set_random_direction()
        elif self.mode == 'eaten':
            self.direction = self.best_direction(self.get_valid_directions(self.node),
                                                 self.init_node.position)

    def set_goal(self, pacman):
        # if self.goal_reached():
        if pacman.direction is not STOP:
            noise = (pacman.direction, OPPOSITE_DIRECTIONS[pacman.direction])[random.randint(0, 1)]
            self.goal = pacman.position.copy() + noise * BOTSIZE[0]

    def goal_reached(self):
        if (self.position - self.goal).normL2() <= self.radius:
            return True
        return False

    def check_mode(self):
        if self.mode == 'frighten':
            self.speed = Creature.speed / 2
            if self.time >= 200:
                self.regular()
                self.time = 0
            else:
                self.time += 1
        elif self.mode == 'regular':
            self.speed = Creature.speed
        elif self.mode == 'eaten':
            if self.target == self.init_node and self.target_reached():
                self.regular()
            else:
                self.speed = Creature.speed * 2

    def move(self):
        self.check_mode()
        dt = self.clock.tick(30) / 1000
        if self.target_reached():
            if self.target is not None:
                self.node = self.target
            if self.node.type == 'portal':
                self.node = self.node.pair
            self.set_position()
            self.set_direction()
            self.set_target()
        self.position += self.direction * self.speed * dt

    def frighten(self):
        self.mode = 'frighten'

    def regular(self):
        self.mode = 'regular'

    def eaten(self):
        self.mode = 'eaten'


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
    pinky = Ghost(nodes, PINK, 0)
    pinky.create()
    inky = Ghost(nodes, BLUE, 0)
    inky.create()
    clyde = Ghost(nodes, AMBER, 0)
    clyde.create()
    blinky = Ghost(nodes, RED, 0)
    blinky.create()

    while not EXIT:
        if not pacman.alive():
            print('You lose!')
            EXIT = True
        if pellets.count() <= 0:
            print('You won!')
            EXIT = True

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
    print(f'Your score is: {pacman.score}')
    pg.quit()


main()
while True:
    print('Want to play more?')
    more = int(input())
    if more:
        main()
    else:
        break
