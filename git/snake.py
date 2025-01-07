import random
import pygame as pg
import sys
from random import randint, shuffle
import time
import os
from collections import deque
from itertools import islice

# Used to modify the window size, values must be a multiple of 40
screen_width = 1200
screen_height = 800
d = None
window = pg.display.set_mode((screen_width, screen_height))
# Controls where the window appears on the screen
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 30)


class Fruit():

    def __init__(self):

        self.color = pg.Color(139, 0, 0)
        self.width = 20
        self.height = 20
        self.fruit = None
        self.radius = 10

        # The initial position of the fruit is placed randomly on the screen
        self.x = randint(0, screen_width / self.width - 1) * self.width
        self.y = randint(0, screen_height / self.height - 1) * self.height
        
    # Prints the fruit on the screen
    def draw_fruit(self, surface):
        self.fruit = pg.Rect(self.x, self.y, self.width, self.height)
        pg.draw.circle(surface, self.color, (self.x + self.radius, self.y + self.radius), self.radius)

    # Checks whether the snake's head collides with the fruit
    def fruit_collision(self, head):

        return self.fruit.colliderect(head)

    # Finds a new location for a fruit after a collision occurs
    def fruit_position(self):

        flag = True
        while flag:

            # The position of the fruit is chosen randomly
            self.x = randint(0, screen_width/self.width - 1) * self.width
            self.y = randint(0, screen_height/self.height - 1) * self.height

            # Checks whether the new fruit location is already occupied by the snake's body
            if snake.empty_space(self.x, self.y):
                break


class Snake(object):

    def __init__(self):

        self.x = screen_width//2
        self.y = screen_height//2
        self.width = 20
        self.height = 20
        self.head = None
        self.speed = 20
        self.direction = None
        self.body = deque()
        self.segment = deque()
        self.head_color = pg.Color(220, 20, 60)
        self.body_color = pg.Color(57, 255, 20)
        self.outline_color = pg.Color(0, 0, 0)

    # Draws the snake's head and body segments on the screen
    def draw_snake(self, surface):

        if len(self.body) > 0:
            for unit in self.segment:
                pg.draw.rect(surface, self.body_color, unit)
                pg.draw.rect(surface, self.outline_color, unit, 1)
        self.head = pg.Rect(self.x, self.y, self.width, self.height)
        pg.draw.rect(surface, self.head_color, self.head)
        pg.draw.rect(surface, self.outline_color, self.head, 1)

    # Adds a segment to the snake if a collision between the head and fruit occurs
    def snake_size(self):

        if len(self.body) != 0:
            index = len(self.body) - 1
            x = self.body[index][0]
            y = self.body[index][1]
            self.body.append([x, y])
            self.segment.append(pg.Rect(x, y, self.width, self.height))

    # Ends the game in the case where the snake collides with the boundaries or the head collides with a body segment
    def boundary_collision(self):

        # If the head of the snake collides with a body segment the function returns True
        # The head collides with the first 2 body segments, count prevents it from registering as a collision
        count = 0
        for part in islice(self.segment, 1):
            if self.head.colliderect(part):
                return True
            count += 1

        # Checks if the head of the snake lies outside of the boundaries of the window
        if self.y < 0 or self.y > screen_height - self.height or self.x < 0 or self.x > screen_width - self.width:
            return True

    # Allows the snake to move and follow the coordinates of the hamiltonian cycle
    def movement(self):

        if self.direction == 'up':
            self.y -= self.speed
        if self.direction == 'down':
            self.y += self.speed
        if self.direction == 'right':
            self.x += self.speed
        if self.direction == 'left':
            self.x -= self.speed

        # Movement is simulated by removing the tail block and adding a block that overlaps with the snake head
        if len(self.body) > 0:
            self.body.pop()
            self.segment.pop()
        self.body.appendleft([self.x, self.y])
        self.segment.appendleft(pg.Rect(self.x, self.y, self.width, self.height))

    # Changes the orientation of movement
    # A snake moving in one direction cannot move in the opposite direction as it would collide with its body
    def change_direction(self, direction):

        if direction == 'up' and self.direction != 'down':
            self.direction = 'up'
        if direction == 'down' and self.direction != 'up':
            self.direction = 'down'
        if direction == 'right' and self.direction != 'left':
            self.direction = 'right'
        if direction == 'left' and self.direction != 'right':
            self.direction = 'left'

    # Checks whether a new fruit position conflicts with a body segment of the snake
    def empty_space(self, x_coordinate, y_coordinate):

        if [x_coordinate, y_coordinate] not in self.body:
            return True
        else:
            return False

def prim_lines(window): 
    global d
    for row in range(40): # w600, r400
        row = (row)*20
        pg.draw.line(window, (0, 255, 0), (row, 0), (row, 400), 1)
    for col in range(20): # w600, r400
        col = (col)*20
        pg.draw.line(window, (0, 255, 0), (0, col), (600, col), 1)
    for key, value in d.items():
        x, y = key
        x = (x+.5)*40
        y = (y+.5)*40
        x_af = x+40
        y_af = y+40
        for i in value:
            if i == "right":
                pg.draw.line(window, (255, 0, 0), (x, y), (x_af, y), 3)
            elif i == "down":
                pg.draw.line(window, (255, 0, 0), (x, y), (x, y_af), 3)
        

# Controls the graphics
# Controls the movement of the snake to follow the hamiltonian cycle
def gameplay(fruit, snake, cycle):
    # Identifies the starting position of the snake
    position = (int(snake.x/20), int(snake.y/20))

    # Identifies the position in the hamiltonian cycle at which the snake begins
    index = cycle.index(position)

    length = len(cycle)
    run = True

    # Loop simulates the movement of the snake and controls game mechanics
    while run:

        # Controls the frame rate of the graphics to make movement smooth and modify the speed of the simulation
        clock = pg.time.Clock()
        clock.tick()

        # If the user clicks the exit button the program closes
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        # Movement is simulated by making screen black and redrawing the snake and fruit
        window.fill(pg.Color(0, 0, 0))
        snake.draw_snake(window)
        fruit.draw_fruit(window)
        prim_lines(window)

        # Finds the direction for the snake's next movement according to the calculated hamiltonian cycle
        if index + 1 < length and cycle[index+1] == (position[0] + 1, position[1]):
            snake.change_direction('right')
            position = (position[0] + 1, position[1])
        elif index + 1 < length and cycle[index+1] == (position[0] - 1, position[1]):
            snake.change_direction('left')
            position = (position[0] - 1, position[1])
        elif index + 1 < length and cycle[index+1] == (position[0], position[1] + 1):
            snake.change_direction('down')
            position = (position[0], position[1] + 1)
        elif index + 1 < length and cycle[index+1] == (position[0], position[1] - 1):
            snake.change_direction('up')
            position = (position[0], position[1] - 1)

        # Takes care of boundary case where the next index of the cycle does not exist
        # The next position is 1st index of the cycle
        # Otherwise the index is incremented by 1
        if index == length - 1:
            # if cycle[0] == (position[0] + 1, position[1]):
            #     snake.change_direction('right')
            #     position = (position[0] + 1, position[1])
            # elif cycle[0] == (position[0] - 1, position[1]):
            #     snake.change_direction('left')
                # position = (position[0] - 1, position[1])
            # if cycle[0] == (position[0], position[1] + 1):
            #     snake.change_direction('down')
            #     position = (position[0], position[1] + 1)
            # if cycle[0] == (position[0], position[1] - 1):
            snake.change_direction('up')
            position = (position[0], position[1] - 1)
            index = 0
        else:
            index += 1

        # Changes the coordinates of the snake's position
        snake.movement()

        # If the snake's head collides with a fruit
        if fruit.fruit_collision(snake.head):

            # A new fruit is generated and the size of the snake is increased by 1
            if len(snake.body) < length:
                fruit.fruit_position()
                snake.snake_size()

            # Once the snake fills up the entire grid there are no more positions for the fruit
            # The game ends and closes
            else:
                time.sleep(3)
                pg.quit()
                sys.exit()

        # Ends the game if the snakes collides with itself or the boundaries
        if snake.boundary_collision():
            time.sleep(3)
            pg.quit()
            sys.exit()

        # Draws all elements on the window
        pg.display.update()


# Uses prim's algorithm to generate a randomized maze using randomized edge weights
def prim_maze_generator(grid_rows, grid_columns):

    directions = dict()
    vertices = grid_rows * grid_columns
    # Creates keys for the directions dictionary
    # Note that the maze has half the width and length of the grid for the hamiltonian cycle
    for i in range(grid_rows):
        for j in range(grid_columns):
            directions[j, i] = []
    # The initial cell for maze generation is chosen randomly
    x = randint(0, grid_columns - 1)
    y = randint(0, grid_rows - 1)
    initial_cell = (x, y)

    current_cell = initial_cell

    # Stores all cells that have been visited
    visited = [initial_cell]
    # print(initial_cell)

    # Contains all neighbouring cells to cells that have been visited
    adjacent_cells = set()

    # Generates walls in grid randomly to create a randomized maze
    while len(visited) != vertices:

        # Stores the position of the current cell in the grid
        x_position = current_cell[0]
        y_position = current_cell[1]
        
        # print(adjacent_cells)
        # Finds adjacent cells when the current cell does not lie on the edge of the grid
        if x_position != 0 and y_position != 0 and x_position != grid_columns - 1 and y_position != grid_rows - 1:
            adjacent_cells.add((x_position, y_position - 1))
            adjacent_cells.add((x_position, y_position + 1))
            adjacent_cells.add((x_position - 1, y_position))
            adjacent_cells.add((x_position + 1, y_position))

        # Finds adjacent cells when the current cell lies in the left top corner of the grid
        elif x_position == 0 and y_position == 0:
            adjacent_cells.add((x_position + 1, y_position))
            adjacent_cells.add((x_position, y_position + 1))

        # Finds adjacent cells when the current cell lies in the bottom left corner of the grid
        elif x_position == 0 and y_position == grid_rows - 1:
            adjacent_cells.add((x_position, y_position - 1))
            adjacent_cells.add((x_position + 1, y_position))

        # Finds adjacent cells when the current cell lies in the left column of the grid
        elif x_position == 0:
            adjacent_cells.add((x_position, y_position - 1))
            adjacent_cells.add((x_position, y_position + 1))
            adjacent_cells.add((x_position + 1, y_position))

        # Finds adjacent cells when the current cell lies in the top right corner of the grid
        elif x_position == grid_columns - 1 and y_position == 0:
            adjacent_cells.add((x_position, y_position + 1))
            adjacent_cells.add((x_position - 1, y_position))
        # Finds adjacent cells when the current cell lies in the bottom right corner of the grid
        elif x_position == grid_columns - 1 and y_position == grid_rows - 1:
            adjacent_cells.add((x_position, y_position - 1))
            adjacent_cells.add((x_position - 1, y_position))

        # Finds adjacent cells when the current cell lies in the right column of the grid
        elif x_position == grid_columns - 1:
            adjacent_cells.add((x_position, y_position - 1))
            adjacent_cells.add((x_position, y_position + 1))
            adjacent_cells.add((x_position - 1, y_position))

        # Finds adjacent cells when the current cell lies in the top row of the grid
        elif y_position == 0:
            adjacent_cells.add((x_position, y_position + 1))
            adjacent_cells.add((x_position - 1, y_position))
            adjacent_cells.add((x_position + 1, y_position))

        # Finds adjacent cells when the current cell lies in the bottom row of the grid
        else:
            adjacent_cells.add((x_position, y_position - 1))
            adjacent_cells.add((x_position + 1, y_position))
            adjacent_cells.add((x_position - 1, y_position))

        # Generates a wall between two cells in the grid
        # adjacent_cells = list(adjacent_cells)
        # random.shuffle(adjacent_cells)
        while current_cell:

            current_cell = (adjacent_cells.pop())
            # The neighbouring cell is disregarded if it is already a wall in the maze
            if current_cell not in visited:

                # The neighbouring cell is now classified as having been visited
                visited.append(current_cell)
                x = current_cell[0]
                y = current_cell[1]
                # To generate a wall, a cell adjacent to the current cell must already have been visited
                # The direction of the wall between cells is stored
                # The process is simplified by only considering a wall to be to the right or down
                if (x + 1, y) in visited:
                    # print("1")
                    directions[x, y] += ['right']
                elif (x - 1, y) in visited:
                    directions[x-1, y] += ['right']
                    # print("2")
                elif (x, y + 1) in visited:
                    # print("3")
                    directions[x, y] += ['down']
                elif (x, y - 1) in visited:
                    # print("4")
                    directions[x, y-1] += ['down']
                # print(f"{(x, y - 1) in visited}\n{(x, y + 1) in visited}\n{(x - 1, y) in visited}\n{(x + 1, y) in visited}")
                # print((x, y) in directions.keys())

                # print((x, y), directions[x, y])
                # print((x-1, y), directions[x-1, y])
                # print((x, y-1), directions[x, y-1])
                # print(adjacent_cells)
                # input()

                break
    
        # adjacent_cells = set(adjacent_cells)


    # Provides the hamiltonian cycle generating algorithm with the direction of the walls to avoid
    # print(directions)
    # directions = {(0, 0): ['right'], (1, 0): ['right'], (2, 0): ['down'], (3, 0): ['right'], (4, 0): ['down'], (5, 0): ['right'], (6, 0): ['down', 'right'], (7, 0): ['right'], (8, 0): ['right'], (9, 0): ['right'], (10, 0): ['right'], (11, 0): ['right'], (12, 0): ['right'], (13, 0): ['right'], (14, 0): [], (0, 1): ['right'], (1, 1): ['right'], (2, 1): ['down'], (3, 1): ['right'], (4, 1): ['down'], (5, 1): ['right'], (6, 1): ['down', 'right'], (7, 1): ['right'], (8, 1): ['right'], (9, 1): ['right'], (10, 1): ['right'], (11, 1): ['right'], (12, 1): ['right'], (13, 1): ['right'], (14, 1): [], (0, 2): ['right'], (1, 2): ['right'], (2, 2): ['down'], (3, 2): ['right'], (4, 2): ['down', 'right'], (5, 2): ['right'], (6, 2): ['right'], (7, 2): ['right'], (8, 2): ['right'], (9, 2): ['right'], (10, 2): ['right'], (11, 2): ['right'], (12, 2): ['right'], (13, 2): ['right'], (14, 2): [], (0, 3): ['right'], (1, 3): ['right'], (2, 3): ['right', 'down'], (3, 3): ['right'], (4, 3): ['right'], (5, 3): ['right'], (6, 3): ['right'], (7, 3): ['right'], (8, 3): ['right'], (9, 3): ['right'], (10, 3): ['right'], (11, 3): ['right'], (12, 3): ['right'], (13, 3): ['right'], (14, 3): [], (0, 4): ['right'], (1, 4): ['right'], (2, 4): ['right', 'down'], (3, 4): ['right'], (4, 4): ['right'], (5, 4): ['right'], (6, 4): ['right'], (7, 4): ['right'], (8, 4): ['right'], (9, 4): ['right'], (10, 4): ['right'], (11, 4): ['right'], (12, 4): ['right'], (13, 4): ['right'], (14, 4): [], (0, 5): ['right'], (1, 5): ['right'], (2, 5): ['right'], (3, 5): ['right', 'down'], (4, 5): ['right'], (5, 5): ['right'], (6, 5): ['right'], (7, 5): ['right'], (8, 5): ['right'], (9, 5): ['right'], (10, 5): [], (11, 5): ['right'], (12, 5): ['down', 'right'], (13, 5): ['right'], (14, 5): [], (0, 6): ['right'], (1, 6): ['right'], (2, 6): ['right'], (3, 6): ['down', 'right'], (4, 6): ['right'], (5, 6): ['right', 'down'], (6, 6): ['right'], (7, 6): ['right'], (8, 6): ['right'], (9, 6): ['right'], (10, 6): ['down', 'right'], (11, 6): ['right'], (12, 6): ['right'], (13, 6): ['right'], (14, 6): [], (0, 7): ['right'], (1, 7): ['right'], (2, 7): ['right'], (3, 7): ['down'], (4, 7): ['right'], (5, 7): ['right', 'down'], (6, 7): ['right'], (7, 7): ['right'], (8, 7): [], (9, 7): ['right'], (10, 7): ['right', 'down'], (11, 7): ['right'], (12, 7): ['right'], (13, 7): ['right'], (14, 7): [], (0, 8): ['right'], (1, 8): ['right'], (2, 8): ['right'], (3, 8): ['down'], (4, 8): ['right'], (5, 8): ['right', 'down'], (6, 8): ['right'], (7, 8): ['right'], (8, 8): [], (9, 8): ['right'], (10, 8): ['down', 'right'], (11, 8): ['right'], (12, 8): ['right'], (13, 8): ['right'], (14, 8): [], (0, 9): ['right'], (1, 9): ['right'], (2, 9): ['right'], (3, 9): [], (4, 9): ['right'], (5, 9): ['right'], (6, 9): ['right'], (7, 9): ['right'], (8, 9): [], (9, 9): ['right'], (10, 9): ['right'], (11, 9): ['right'], (12, 9): ['right'], (13, 9): ['right'], (14, 9): []}
    global d
    d = directions
    print(directions)
    print("\n\n\n\n\n")
    return hamiltonian_cycle(grid_rows, grid_columns, directions)




# Finds a hamiltonian cycle for the snake to follow to prevent collisions with its body segments
# Note that the grid for the hamiltonian cycle is double the width and height of the grid for the maze
def hamiltonian_cycle(grid_rows, grid_columns, orientation):
    # The path for the snake is stored in a dictionary
    # The keys are the (x, y) positions in the grid
    # The values are the adjacent (x, y) positions that the snake can travel towards
    hamiltonian_graph = dict()
    for i in range(grid_rows*2):
        for j in range(grid_columns*2):
            hamiltonian_graph[j, i] = []
    print(f"rows {grid_rows} col: {grid_columns}")
    # Uses the coordinates of the walls to generate available adjacent cells for each cell
    # Simplified by only considering the right and down directions
    for i in range(grid_rows):
        for j in range(grid_columns):
            # Finds available adjacent cells if current cell does not lie on an edge of the grid
            if j != grid_columns - 1 and i != grid_rows - 1 and j != 0 and i != 0:
                if 'right' in orientation[j, i]:
                    hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 2, i*2)]
                    hamiltonian_graph[j*2 + 1, i*2 + 1] = [(j*2 + 2, i*2 + 1)]
                else:
                    hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 1, i*2 + 1)]
                if 'down' in orientation[j, i]:
                    hamiltonian_graph[j*2, i*2 + 1] = [(j*2, i*2 + 2)]
                    hamiltonian_graph[j * 2 + 1, i * 2 + 1] += [(j * 2 + 1, i * 2 + 2)]
                    # if (j*2 + 1, i*2 + 1) in hamiltonian_graph:
                    #     hamiltonian_graph[j * 2 + 1, i * 2 + 1] += [(j * 2 + 1, i * 2 + 2)]
                    # else:
                    #     hamiltonian_graph[j*2 + 1, i*2 + 1] = [(j*2 + 1, i*2 + 2)]
                else:
                    hamiltonian_graph[j*2, i*2 + 1] = [(j*2 + 1, i*2 + 1)]
                if 'down' not in orientation[j, i-1]: # Connects bottom right box
                    hamiltonian_graph[j*2, i*2] = [(j*2 + 1, i*2)]
                if 'right' not in orientation[j-1, i]:
                    hamiltonian_graph[j * 2, i * 2] += [(j * 2, i * 2 + 1)] # Connects left to right box
                #     # if (j*2, i*2) in hamiltonian_graph: # useless if statement
                #     #     print(hamiltonian_graph[j*2, i*2])
                #     #     hamiltonian_graph[j * 2, i * 2] += [(j * 2, i * 2 + 1)]
                #     # else:
                #     #     hamiltonian_graph[j*2, i*2] = [(j*2, i*2 + 1)]

            # Finds available adjacent cells if current cell is in the bottom right corner
            elif j == grid_columns - 1 and i == grid_rows - 1:
                hamiltonian_graph[j*2, i*2 + 1] = [(j*2 + 1, i*2 + 1)]
                hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 1, i*2 + 1)]
                if 'down' not in orientation[j, i-1]:
                    hamiltonian_graph[j*2, i*2] = [(j*2 + 1, i*2)]
                elif 'right' not in orientation[j-1, i]:
                    hamiltonian_graph[j*2, i*2] = [(j*2, i*2 + 1)] 

            # Finds available adjacent cells if current cell is in the top right corner
            elif j == grid_columns - 1 and i == 0:
                hamiltonian_graph[j*2, i*2] = [(j*2 + 1, i*2)]
                hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 1, i*2 + 1)]
                if 'down' in orientation[j, i]:
                    hamiltonian_graph[j*2, i*2 + 1] = [(j*2, i*2 + 2)]
                    hamiltonian_graph[j*2 + 1, i*2 + 1] = [(j*2 + 1, i*2 + 2)]
                else:
                    hamiltonian_graph[j*2, i*2 + 1] = [(j*2 + 1, i*2 + 1)]
                if 'right' not in orientation[j-1, i]:
                    hamiltonian_graph[j*2, i*2] = [(j*2, i*2 + 1)]

            # Finds available adjacent cells if current cell is in the right column
            elif j == grid_columns - 1:
                hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 1, i*2 + 1)]
                if 'down' in orientation[j, i]:
                    hamiltonian_graph[j*2, i*2 + 1] = [(j*2, i*2 + 2)]
                    hamiltonian_graph[j*2 + 1, i*2 + 1] = [(j*2 + 1, i*2 + 2)]
                else:
                    hamiltonian_graph[j*2, i*2 + 1] = [(j*2 + 1, i*2 + 1)]
                if 'down' not in orientation[j, i-1]:
                    hamiltonian_graph[j*2, i*2] = [(j*2 + 1, i*2)]
                if 'right' not in orientation[j-1, i]:
                    if (j*2, i*2) in hamiltonian_graph:
                        hamiltonian_graph[j * 2, i * 2] += [(j * 2, i * 2 + 1)]
                    else:
                        hamiltonian_graph[j*2, i*2] = [(j*2, i*2 + 1)]

            # Finds available adjacent cells if current cell is in the top left corner
            elif j == 0 and i == 0:
                hamiltonian_graph[j*2, i*2] = [(j*2 + 1, i*2)]
                hamiltonian_graph[j*2, i*2] += [(j*2, i*2 + 1)]
                if 'right' in orientation[j, i]:
                    hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 2, i*2)]
                    hamiltonian_graph[j*2 + 1, i*2 + 1] = [(j*2 + 2, i*2 + 1)]
                else:
                    hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 1, i*2 + 1)]
                if 'down' in orientation[j, i]:
                    hamiltonian_graph[j*2, i*2 + 1] = [(j*2, i*2 + 2)]
                    hamiltonian_graph[j * 2 + 1, i * 2 + 1] += [(j * 2 + 1, i * 2 + 2)]
                else:
                    hamiltonian_graph[j*2, i*2 + 1] = [(j*2 + 1, i*2 + 1)]

            # Finds available adjacent cells if current cell is in the bottom left corner
            elif j == 0 and i == grid_rows - 1:
                hamiltonian_graph[j*2, i*2] = [(j*2, i*2 + 1)]
                hamiltonian_graph[j*2, i*2 + 1] = [(j*2 + 1, i*2 + 1)]
                if 'right' in orientation[j, i]:
                    hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 2, i*2)]
                    hamiltonian_graph[j*2 + 1, i*2 + 1] = [(j*2 + 2, i*2 + 1)]
                else:
                    hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 1, i*2 + 1)]
                if 'down' not in orientation[j, i-1]:
                    hamiltonian_graph[j * 2, i * 2] += [(j * 2 + 1, i * 2)]

            # Finds available adjacent cells if current cell is in the left corner
            elif j == 0:
                hamiltonian_graph[j*2, i*2] = [(j*2, i*2 + 1)]
                if 'right' in orientation[j, i]:
                    hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 2, i*2)]
                    hamiltonian_graph[j*2 + 1, i*2 + 1] = [(j*2 + 2, i*2 + 1)]
                else:
                    hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 1, i*2 + 1)]
                if 'down' in orientation[j, i]:
                    hamiltonian_graph[j*2, i*2 + 1] = [(j*2, i*2 + 2)]
                    if (j*2 + 1, i*2 + 1) in hamiltonian_graph:
                        hamiltonian_graph[j*2 + 1, i*2 + 1] += [(j*2 + 1, i*2 + 2)]
                    else:
                        hamiltonian_graph[j * 2 + 1, i * 2 + 1] = [(j * 2 + 1, i * 2 + 2)]
                else:
                    hamiltonian_graph[j*2, i*2 + 1] = [(j*2 + 1, i*2 + 1)]
                if 'down' not in orientation[j, i-1]:
                    hamiltonian_graph[j*2, i*2] += [(j*2 + 1, i*2)]

            # Finds available adjacent cells if current cell is in the top row
            elif i == 0:
                hamiltonian_graph[j*2, i*2] = [(j*2 + 1, i*2)]
                if 'right' in orientation[j, i]:
                    hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 2, i*2)]
                    hamiltonian_graph[j*2 + 1, i*2 + 1] = [(j*2 + 2, i*2 + 1)]
                else:
                    hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 1, i*2 + 1)]
                if 'down' in orientation[j, i]:
                    hamiltonian_graph[j*2, i*2 + 1] = [(j*2, i*2 + 2)]
                    if (j*2 + 1, i*2 + 1) in hamiltonian_graph:
                        hamiltonian_graph[j * 2 + 1, i * 2 + 1] += [(j * 2 + 1, i * 2 + 2)]
                    else:
                        hamiltonian_graph[j*2 + 1, i*2 + 1] = [(j*2 + 1, i*2 + 2)]
                else:
                    hamiltonian_graph[j*2, i*2 + 1] = [(j*2 + 1, i*2 + 1)]
                if 'right' not in orientation[j-1, i]:
                    hamiltonian_graph[j*2, i*2] += [(j*2, i*2 + 1)]

            # Finds available adjacent cells if current cell is in the bottom row
            else:
                hamiltonian_graph[j*2, i*2 + 1] = [(j*2 + 1, i*2 + 1)]
                if 'right' in orientation[j, i]:
                    hamiltonian_graph[j*2 + 1, i*2 + 1] = [(j*2 + 2, i*2 + 1)]
                    hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 2, i*2)]
                else:
                    hamiltonian_graph[j*2 + 1, i*2] = [(j*2 + 1, i*2 + 1)]
                if 'down' not in orientation[j, i-1]:
                    hamiltonian_graph[j*2, i*2] = [(j*2 + 1, i*2)]
                if 'right' not in orientation[j-1, i]:
                    if (j*2, i*2) in hamiltonian_graph:
                        hamiltonian_graph[j*2, i*2] += [(j*2, i*2 + 1)]
                    else:
                        hamiltonian_graph[j * 2, i * 2] = [(j * 2, i * 2 + 1)]

    # Provides the coordinates of available adjacent cells to generate directions for the snake's movement
    #print(hamiltonian_graph)
    print(hamiltonian_graph)
    return path_generator(hamiltonian_graph, grid_rows*grid_columns*4)


# Generates a path composed of coordinates for the snake to travel along
# def path_generator(graph, cells):
#     # The starting position for the path is at cell (0, 0)
#     path = [(0, 0)]

#     previous_cell = path[0]
#     previous_direction = None

#     # Generates a path that is a hamiltonian cycle by following a set of general laws
#     # 1. If the right cell is available, travel to the right
#     # 2. If the cell underneath is available, travel down
#     # 3. If the left cell is available, travel left
#     # 4. If the cell above is available, travel up
#     # 5. The current direction cannot oppose the previous direction (e.g. left --> right)
#     while len(path) != cells:
#         if (previous_cell[0] + 1, previous_cell[1]) in graph[previous_cell] \
#                 and previous_direction != 'left':
#             path.append((previous_cell[0] + 1, previous_cell[1]))
#             previous_cell = (previous_cell[0] + 1, previous_cell[1])
#             previous_direction = 'right'
#         elif (previous_cell[0], previous_cell[1] + 1) in graph[previous_cell]  \
#                 and previous_direction != 'up':
#             path.append((previous_cell[0], previous_cell[1] + 1))
#             previous_cell = (previous_cell[0], previous_cell[1] + 1)
#             previous_direction = 'down'
#         elif (previous_cell[0] - 1, previous_cell[1]) in graph \
#                 and previous_cell in graph[previous_cell[0] - 1, previous_cell[1]] and previous_direction != 'right':
#             path.append((previous_cell[0] - 1, previous_cell[1]))
#             previous_cell = (previous_cell[0] - 1, previous_cell[1])
#             previous_direction = 'left'
#         elif (previous_cell[0], previous_cell[1]-1) in graph \
#                 and previous_cell in graph[previous_cell[0], previous_cell[1]-1] and previous_direction != "down":
#             path.append((previous_cell[0], previous_cell[1] - 1))
#             previous_cell = (previous_cell[0], previous_cell[1] - 1)
#             previous_direction = 'up'
#     return path

#     # Returns the coordinates of the hamiltonian cycle path
#     return path

def path_generator(cycle, cells):
    path = [(0, 0)]
    x, y = (0, 0)
    last_dir = None

    while len(path) != cells:
        if (x+1, y) in cycle and (x+1, y) in cycle[x, y] and last_dir != "left":
            path.append((x+1, y))
            x, y = (x+1, y)
            last_dir = "right"
        elif (x, y+1) in cycle and (x, y+1) in cycle[x, y] and last_dir != "up":
            path.append((x, y+1))
            x, y = (x, y+1)
            last_dir = "down"
        elif (x-1, y) in cycle and (x, y) in cycle[x-1, y] and last_dir != "right":
            path.append((x-1, y))
            x, y = (x-1, y)
            last_dir = "left"
        elif (x, y-1) in cycle and (x, y) in cycle[x, y-1] and last_dir != "down":
            path.append((x, y-1))
            x, y = (x, y-1)
            last_dir = "up"
        else:
            print("You suck at coding")

    return path



fruit = Fruit()
snake = Snake()
def main():
    # if __name__ == "__main__":
    circuit = prim_maze_generator(int(screen_height/40), int(screen_width/40))
    pg.init()
    # window = pg.display.set_mode((screen_width, screen_height))
    pg.display.set_caption('Snake Solver')
    gameplay(fruit, snake, circuit)
main()