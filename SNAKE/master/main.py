import pygame as pg
from random import randint, shuffle, choice
from collections import deque
import sys
import os
import time
import exceptions

# Screen dimensions must be a multiple of 40
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600

# Size of the map cannot be odd both ways
# WIDTH / COLUMNS must equal to ROWS / HEIGHT
COLUMNS = 20
ROWS = 10

CUBE_DIM = int(SCREEN_WIDTH / COLUMNS or SCREEN_HEIGHT / ROWS)

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 30) # Centers window when it appears # 0, 30 OR -1300 220


def check_measurements():

    if ROWS % 2 and COLUMNS % 2:
        raise exceptions.InvalidMeasurements("Impossible map, change map size")
    if SCREEN_WIDTH / COLUMNS != SCREEN_HEIGHT / ROWS:
        raise exceptions.InvalidMeasurements("Invalid dimensions for map size")

class Fruit:

    def __init__(self, snake: "Snake") -> None:
        self.color = pg.Color(231, 76, 27) # Default color for Google Snake
        self.unitsize  = CUBE_DIM # Defines the dimensions of the cube
        # Initial position for fruit
        self.x = randint(0, int(SCREEN_WIDTH / self.unitsize - 1)) * self.unitsize
        self.y = randint(0, int(SCREEN_HEIGHT / self.unitsize - 1)) * self.unitsize
        # self.x, self.y = (560, 240)
        self.fruit = pg.Rect(self.x, self.y, self.unitsize, self.unitsize) # Defined later
        self.snake = snake

    # Draws fruit to surface
    def update(self, surface):

        self.fruit = pg.Rect(self.x, self.y, self.unitsize, self.unitsize)
        pg.draw.circle(surface, self.color, (self.x + self.unitsize / 2, self.y + self.unitsize / 2), self.unitsize / 2)

    # Spawns a new fruit
    def spawn_fruit(self):

        while True:
            self.x = randint(0, int(SCREEN_WIDTH / self.unitsize - 1)) * self.unitsize
            self.y = randint(0, int(SCREEN_HEIGHT / self.unitsize - 1)) * self.unitsize

            if self.snake.vacant_unit(self.x, self.y): break

    # Checks if fruit has been eaten
    def collision(self, head) -> bool:
        return self.fruit.colliderect(head)
    

class Snake:

    def __init__(self) -> None:
        self.x = SCREEN_WIDTH // 2 # X Dimension snake head
        self.y = SCREEN_HEIGHT // 2 # Y Dimension snake head
        self.unitsize = CUBE_DIM
        self.head = None
        # Deque allows for appending body parts on both ends of the list
        self.body = deque()
        self.pgbody = deque()
        self.direction = None
        self.BODY_COLOR = pg.Color(0, 255, 0) # Green
        self.HEAD_COLOR = pg.Color(255, 145, 0) # Orange

    # Draws snake to surface
    def update(self, surface):

        if len(self.body) != 0: # Checks if body size is not 0
            for unit in self.pgbody:
                pg.draw.rect(surface, self.BODY_COLOR, unit)
                pg.draw.rect(surface, (0, 0, 0), unit, width=2)
        self.head = pg.Rect(self.x, self.y, self.unitsize, self.unitsize)
        pg.draw.rect(surface, (0, 0, 0), self.head, width=2)
        pg.draw.rect(surface, self.HEAD_COLOR, self.head)
    
    # Adds a unit if it collides with fruit
    def extend(self):

        if len(self.body) != 0: # Checks if body size is not 0
            index = len(self.body) -1
            x, y = self.body[index]
            self.body.append((x, y))
            self.pgbody.append(pg.Rect(x, y, self.unitsize, self.unitsize))
    
    # Ends game if it collides with its own body or walls
    def check_collision(self) -> bool:

        # If a body part overlaps the head then it returns True
        i = 0
        for unit in self.pgbody:
            if self.head.colliderect(unit) and i > 2:
                return True
            i += 1
        
        # Checks if snake hits a wall
        if self.y < 0 or self.y > SCREEN_HEIGHT - self.unitsize or self.x < 0 or self.x > SCREEN_WIDTH - self.unitsize:
            return True
    
    def update_movement(self):
        # Changes direction based on cycle
        if self.direction == "up":
            self.y -= self.unitsize
        if self.direction == "down":
            self.y += self.unitsize
        if self.direction == "left":
            self.x -= self.unitsize
        if self.direction == "right":
            self.x += self.unitsize

        # The tail is popped off and the head is appened to simulate movement
        if len(self.body) != 0: # Checks if body size is not 0
            self.body.pop()
            self.pgbody.pop()
        # Body is read from left to right not right to left
        self.body.appendleft((self.x, self.y))
        self.pgbody.appendleft(pg.Rect(self.x, self.y, self.unitsize, self.unitsize))

    # Checks if the space is vacant
    def vacant_unit(self, x, y) -> bool:
        return (x, y) not in self.body
    
    def change_dir(self, direction):
        # Changes direction and makes sure that it is not going the opposite direction of it current path
        if direction == 'up' and self.direction != "down":
            self.direction = "up"
        if direction == "down" and self.direction != "up":
            self.direction = "down"
        if direction == 'left' and self.direction != 'right':
            self.direction = 'left'
        if direction == 'right' and self.direction != 'left':
            self.direction = 'right'


class AI:

    def __init__(self, window, fruit: "Fruit", snake: "Snake", path, maze, dev: "DeveloperTools", columns, rows) -> None:
        self.surface = window
        self.fruit = fruit
        self.snake = snake
        self.path = path # DONT EDIT
        self.maze = maze
        self.x, self.y = (int(snake.x/CUBE_DIM), int(snake.y/CUBE_DIM)) # Snake Head
        self.index = self.path.index((self.x, self.y))
        self.last_direction = None
        self.score = 1
        self.font = pg.font.SysFont("arial", 12)
        self.config = dev
        self.body = list()
        self.columns = columns
        self.rows = rows
        self.empty_spaces = list() # Used to be copied later on in check_hamiltonicity()
        
        for x in range(COLUMNS):
            for y in range(ROWS):
                self.empty_spaces.append((x, y))
        
    



    def check_hamiltonicity(self):
        if (self.x, self.y) != (self.snake.x // 60, self.snake.y // 60): # Debugger
            raise Exception(f"{self.index}, {len(self.path)}\nNOT EVEN {(self.x, self.y)} SNAKE PIX {(self.snake.x // 60, self.snake.y // 60)}")

        connected_units = dict()
        possible_moves = {"up": (self.x, self.y-1), "down": (self.x, self.y+1), "left": (self.x-1, self.y), "right": (self.x+1, self.y)} # All possible moves for the snake
        for direction, head in possible_moves.items():
            connected_units[direction] = True
            visited = list() # Units already checked
            awaited_units = list() # Units adjacent to visited units to be checked next

            if head not in self.body and 0 <= head[0] <= COLUMNS-1 and 0 <= head[1] <= ROWS-1: # Checks if head isn't part of the body or off the grid, to save CPU resources
                vacant_spaces = self.empty_spaces.copy() # Contains all empty spaces AFTER body movement has been simulated
                
                
                vacant_spaces.remove((head)) # Adds a head to simulate movement
                for unit in list(self.body)[:-1]: # Removes body but tail remains to simulate movement
                    vacant_spaces.remove((unit))
                
                start_unit = (choice(vacant_spaces))
                visited.append(start_unit)
                awaited_units.append(start_unit)
                flag = True # Walrus operator not used
                while flag:
                    adjacent_units = set()
                    for x, y in awaited_units:
                        reachable_units = set() # Contains units reachable by the current unit
 
                        if (x+1, y) in vacant_spaces and (x+1, y) not in visited and x+1 <= self.columns-1: # Right
                            adjacent_units.add((x+1, y))
                            # print("R")

                        if (x-1, y) in vacant_spaces and (x-1, y) not in visited and x-1 >= 0: # Left
                            adjacent_units.add((x-1, y))
                            # print("L")
                        if (x, y-1) in vacant_spaces and (x, y-1) not in visited and y-1 >= 0: # Up
                            adjacent_units.add((x, y-1))
                            # print("U")
                        if (x, y+1) in vacant_spaces and (x, y+1) not in visited and y+1 <= self.rows-1: # Down
                            adjacent_units.add((x, y+1))
                            # print("D")

                        # Checks for second to last unit because movement is simulated ( If length is 1 )
                        # self.body[-2] is needed since the tail and head are able to have a one way in / out passage, and there is movement temp
                        if len(self.body) >= 2:
                            if (x+1, y) in vacant_spaces or (x+1, y) == self.body[-2] or (x+1, y) == head and x+1 <= self.columns-1: # Right
                                reachable_units.add((x+1, y))

                            if (x-1, y) in vacant_spaces or (x-1, y) == self.body[-2] or (x-1, y) == head and x-1 >= 0: # Left
                                reachable_units.add((x-1, y))

                            if (x, y-1) in vacant_spaces or (x, y-1) == self.body[-2] or (x, y-1) == head and y-1 >= 0: # Up
                                reachable_units.add((x, y-1))

                            if (x, y+1) in vacant_spaces or (x, y+1) == self.body[-2] or (x, y+1) == head and y+1 <= self.rows-1: # Down
                                reachable_units.add((x, y+1))

                            if len(reachable_units) < 2:
                                print(f"'{len(reachable_units)}' reachable_units AT {reachable_units}\nLooking at {head} area\n HEAD IS CURRENTLY AT {(self.x, self.y)}\nERROR AT {(x, y)}\n'{direction}' direction is not availible")
                                connected_units[direction] = False
                                flag = False
                                break

                        

                        

                    if not len(adjacent_units) and flag: # Adj units == 0 or not possible adj units left
                        if len(visited) == len(vacant_spaces): # Passed test, snake can go on it's merry way
                            connected_units[direction] = True
                        else:
                            connected_units[direction] = False
                            print(f"Failed cutoff test {direction}")
                            # print(f"v: {len(visited)}, vs: {len(vacant_spaces)}")
                            # print(list(set(vacant_spaces)-set(visited)))
                            # input(f"{direction} + {coords}")
                        break

                    else:
                        visited += adjacent_units
                        awaited_units = adjacent_units
                    
                    # Head Special Case
                    x, y = (head)

                    head_adjacent_units = set()
                    head_illegal_moves = set()
                    if (x+1, y) in vacant_spaces and x+1 <= self.columns-1: # Right
                        head_adjacent_units.add((x+1, y))
                        # print("R")
                    if (x-1, y) in vacant_spaces and x-1 >= 0: # Left
                        head_adjacent_units.add((x-1, y))
                        # print("L")
                    if (x, y-1) in vacant_spaces and y-1 >= 0: # Up
                        head_adjacent_units.add((x, y-1))
                        # print("U")
                    if (x, y+1) in vacant_spaces and y+1 <= self.rows-1: # Down
                        head_adjacent_units.add((x, y+1))
                        # print("D")

                    for hx, hy in head_adjacent_units:
                        head_reachable_units = set()
                        if (hx+1, hy) in vacant_spaces and hx+1 <= self.columns-1: # Right
                            head_reachable_units.add((hx+1, hy))

                        if (hx-1, hy) in vacant_spaces and hx-1 >= 0: # Left
                            head_reachable_units.add((hx-1, hy))

                        if (hx, hy-1) in vacant_spaces and hy-1 >= 0: # Up
                            head_reachable_units.add((hx, hy-1))

                        if (hx, hy+1) in vacant_spaces and hy+1 <= self.rows-1: # Down
                            head_reachable_units.add((hx, hy+1))
                        
                        if len(head_reachable_units) == 1:
                            head_illegal_moves.add(f"{(hx, hy)}, EXTRA: {head_reachable_units}")

                    if len(head_illegal_moves) > 1:
                        print(f"ILLEGAL MOVE: {len(head_illegal_moves)} {head_illegal_moves} AT {head}, CURRENTLY AT {(self.x, self.y)} DIRECTION {direction}, SNAKE {(self.snake.x // 60, self.snake.y // 60)}")
                        connected_units[direction] = False
                        flag = False
                
                


            else: # Illegal move // snake body or wall
                connected_units[direction] = False
        

        # Special algorithm, this will prevent double deadends before it happens, Double-Deadend Precheck Alg
        if connected_units["right"] and (self.x+1, self.y) not in self.body and self.x+1 == self.columns-1 and ((self.x-1, self.y+1) in self.body or (self.x-1, self.y-1) in self.body): # Right
            # input(f"On the right column currently {self.x}, {self.y}, {(self.x-1, self.y+1) in self.body} {(self.x-1, self.y-1) in self.body}")
            return {"up": False, "down": False, "left": False, "right": True}
            # print("R")
        if connected_units["left"] and (self.x-1, self.y) not in self.body and self.x-1 == 0 and ((self.x+1, self.y+1) in self.body or (self.x+1, self.y-1) in self.body): # Left
            # input(f"left {self.x}, {self.y} {(self.x+1, self.y+1) in self.body} {(self.x+1, self.y-1) in self.body}")
            return {"up": False, "down": False, "left": True, "right": False}
            # print("L")
        if connected_units["up"] and (self.x, self.y-1) not in self.body and self.y-1 == 0 and ((self.x+1, self.y-1) in self.body or (self.x-1, self.y-1) in self.body): # Up
            # input(f"Up {self.x}, {self.y} {(self.x+1, self.y-1) in self.body} {(self.x-1, self.y-1) in self.body}")
            return {"up": True, "down": False, "left": False, "right": False}
            # print("U")
        if connected_units["down"] and (self.x, self.y+1) not in self.body and self.y+1 == self.rows-1 and ((self.x+1, self.y+1) in self.body or (self.x-1, self.y+1) in self.body): # Down
            # input(f"Down {self.x}, {self.y} {(self.x+1, self.y+1) in self.body} {(self.x-1, self.y+1) in self.body}")
            return {"up": False, "down": True, "left": False, "right": False}
            # print("D")


        return connected_units


    

    def cheat(self):
        if self.snake.body: self.body = list(map(lambda x: (x[0]//CUBE_DIM, x[1]//CUBE_DIM), self.snake.body))
        # else: self.body = self.snake.body # Empty List
        potential_cheats = dict() # Coords: index
        fx, fy = (fruit.x//CUBE_DIM, fruit.y//CUBE_DIM)
        sx, sy = (snake.x//CUBE_DIM, snake.y//CUBE_DIM)

        # Grab the path from the snake to the apple directly
        findex = self.path.index((fx, fy))
        sindex = self.path.index((sx, sy))
        fruit_collide = (self.snake.x, self.snake.y) == (self.fruit.x, self.fruit.y)
        
        checkmaze = self.check_hamiltonicity() # Checks for hamiltonicity by checking for deadends and prechecks for deadends
        # checkmaze = {"up": True, "down": True, "left": True, "right": True}
        print(f"Hamiltonicity: {checkmaze}\n")
        c = 0
        for i in checkmaze.values():
            if i:
                c += 1
        if not c:
            input("ALL FALSE")
            assert False

        if not fruit_collide and self.index+1 != len(self.path):


            if findex + 1 > sindex:
                pathtofruit = path[sindex:findex+1] # Path directely from snake to fruit
                print("GOING DIRECTLY TO FRUIT")
                try:
                    pathtofruit.pop(1)
                except:
                    print(pathtofruit)
                    input((sindex, findex))
            else:
                # pathtofruit = path[findex:sindex+1]
                print("GOING FROM (0, 0) TO THE FRUIT")
                pathtofruit = path[sindex:] + path[:findex+1] # Path to (0, 0) from the snake and (0, 0) to the fruit
                # pathtofruit = path[findex:sindex+1]
                # pathtofruit.reverse()
                pathtofruit.pop(1)
                # input((len(pathtofruit), pathtofruit))

            if (self.x-1, self.y) in pathtofruit and (self.x-1, self.y) not in self.body and self.last_direction != "right" and self.x-1 >= 0 and checkmaze["left"]: # Left Cheat
                headindex = pathtofruit.index((self.x-1, self.y))
                potential_cheats[headindex] = "left"
                print(f"Left: {self.x, self.y}")

            if (self.x+1, self.y) in pathtofruit and (self.x+1, self.y) not in self.body and self.last_direction != "left" and self.x+1 <= self.columns-1 and checkmaze["right"]: # Right Cheat
                headindex = pathtofruit.index((self.x+1, self.y))
                potential_cheats[headindex] = "right"
                print(f"Right: {self.x, self.y}")

            if (self.x, self.y-1) in pathtofruit and (self.x, self.y-1) not in self.body and self.last_direction != "down" and self.y-1 >= 0 and checkmaze["up"]: # Up Cheat
                headindex = pathtofruit.index((self.x, self.y-1))
                potential_cheats[headindex] = "up" # , path.index((x, y-1))]
                print(f"Up: {self.x, self.y}")

            if (self.x, self.y+1) in pathtofruit and (self.x, self.y+1) not in self.body and self.last_direction != "up" and self.y+1 <= self.rows-1 and checkmaze["down"]: # Down Cheat
                headindex = pathtofruit.index((self.x, self.y+1))
                potential_cheats[headindex] = "down" # , path.index((x, y+1))]
                print(f"Down: {self.x, self.y}")

            if potential_cheats:
                best_index = max(potential_cheats.keys()) # Gets the unit with the farther cheating unit
                self.x, self.y = pathtofruit[best_index]
                self.last_direction = potential_cheats[best_index]
                snake.change_dir(self.last_direction)
                self.index = self.path.index((self.x, self.y)) # Moves index so it doesn't follow its default path
                print(f"{self.index} INDEX NO ERR")
                print(f"Cheating: {sx, sy} --> {self.x, self.y}\nLast Direction: {self.last_direction}\n\n")

            
        if not potential_cheats:
            #if self.index+1 == len(self.path) and self.path[0] in self.body: input(f"SPECIAL CASE {self.index+1 == len(self.path) and self.path[0] not in self.body}, {self.index}, {(self.x, self.y)}") # Special case, ind 0 to last ind
            #  Special case when list ends and is stuck at (0, 1)
            if self.index+1 == len(self.path) and self.path[0] not in self.body:
                print("RESETTING TO (0, 0)")
                snake.change_dir("up")
                self.last_direction = "up"
                print((self.x, self.y))
                self.x, self.y = (self.x, self.y-1)
                print((self.x, self.y, snake.direction))
                self.index = 0

            elif (self.x, self.y) == (0, 0) and self.last_direction != "up": # Special case where snake goes from index 0 to last index
                snake.change_dir("down")
                self.index = len(self.path) - 1
                self.x, self.y = (self.x, self.y+1)
                self.last_direction = "down"

            elif self.index+1 == len(self.path): # When above elif runs, snake must go backwards on the hamiltonian cycle
                if self.path[self.index-1] == (self.x, self.y+1) and self.last_direction != "up" and (self.x, self.y+1) not in self.body and checkmaze["down"]: # Down
                    snake.change_dir("down")
                    self.index -= 1
                    self.x, self.y = (self.x, self.y+1)
                    self.last_direction = "down"
                elif self.path[self.index-1] == (self.x, self.y-1) and self.last_direction != "down" and (self.x, self.y-1) not in self.body and checkmaze["up"]: # Up
                    snake.change_dir("up")
                    self.index -= 1
                    self.x, self.y = (self.x, self.y-1)
                    self.last_direction = "up"
                elif self.path[self.index-1] == (self.x-1, self.y) and self.last_direction != "right" and (self.x-1, self.y) not in self.body and checkmaze["left"]: # Left
                    snake.change_dir("left")
                    self.index -= 1
                    self.x, self.y = (self.x-1, self.y)
                    self.last_direction = "left"
                elif self.path[self.index-1] == (self.x+1, self.y) and self.last_direction != "left" and (self.x+1, self.y) not in self.body and checkmaze["right"]: # Right
                    snake.change_dir("right")
                    self.index -= 1
                    self.x, self.y = (self.x+1, self.y)
                    self.last_direction = "right"
                else:
                    if self.last_direction != "up" and (self.x, self.y+1) not in self.body and checkmaze["down"]: # Down
                        snake.change_dir("down")
                        self.x, self.y = (self.x, self.y+1)
                        self.index = self.path.index((self.x, self.y))
                        self.last_direction = "down"
                    elif self.last_direction != "down" and (self.x, self.y-1) not in self.body and checkmaze["up"]: # Up
                        snake.change_dir("up")
                        self.x, self.y = (self.x, self.y-1)
                        self.index = self.path.index((self.x, self.y))
                        self.last_direction = "up"
                    elif self.last_direction != "right" and (self.x-1, self.y) not in self.body and checkmaze["left"]: # Left
                        snake.change_dir("left")
                        self.x, self.y = (self.x-1, self.y)
                        self.index = self.path.index((self.x, self.y))
                        self.last_direction = "left"
                    elif self.last_direction != "left" and (self.x+1, self.y) not in self.body and checkmaze["right"]: # Right
                        snake.change_dir("right")
                        self.x, self.y = (self.x+1, self.y)
                        self.index = self.path.index((self.x, self.y))
                        self.last_direction = "right"

            # Changes direction
            else:
                print("Running default hamiltonian cycle")

                if self.path[self.index+1] == (self.x, self.y+1) and self.last_direction != "up" and (self.x, self.y+1) not in self.body and checkmaze["down"]: # Down
                    snake.change_dir("down")
                    self.index += 1
                    self.x, self.y = (self.x, self.y+1)
                    self.last_direction = "down"
                elif self.path[self.index+1] == (self.x, self.y-1) and self.last_direction != "down" and (self.x, self.y-1) not in self.body and checkmaze["up"]: # Up
                    snake.change_dir("up")
                    self.index += 1
                    self.x, self.y = (self.x, self.y-1)
                    self.last_direction = "up"
                elif self.path[self.index+1] == (self.x-1, self.y) and self.last_direction != "right" and (self.x-1, self.y) not in self.body and checkmaze["left"]: # Left
                    snake.change_dir("left")
                    self.index += 1
                    self.x, self.y = (self.x-1, self.y)
                    self.last_direction = "left"
                elif self.path[self.index+1] == (self.x+1, self.y) and self.last_direction != "left" and (self.x+1, self.y) not in self.body and checkmaze["right"]: # Right
                    snake.change_dir("right")
                    self.index += 1
                    self.x, self.y = (self.x+1, self.y)
                    self.last_direction = "right"
                else:
                    if self.last_direction != "up" and (self.x, self.y+1) not in self.body and checkmaze["down"]: # Down
                        snake.change_dir("down")
                        self.x, self.y = (self.x, self.y+1)
                        self.index = self.path.index((self.x, self.y))
                        self.last_direction = "down"
                    elif self.last_direction != "down" and (self.x, self.y-1) not in self.body and checkmaze["up"]: # Up
                        snake.change_dir("up")
                        self.x, self.y = (self.x, self.y-1)
                        self.index = self.path.index((self.x, self.y))
                        self.last_direction = "up"
                    elif self.last_direction != "right" and (self.x-1, self.y) not in self.body and checkmaze["left"]: # Left
                        snake.change_dir("left")
                        self.x, self.y = (self.x-1, self.y)
                        self.index = self.path.index((self.x, self.y))
                        self.last_direction = "left"
                    elif self.last_direction != "left" and (self.x+1, self.y) not in self.body and checkmaze["right"]: # Right
                        snake.change_dir("right")
                        self.x, self.y = (self.x+1, self.y)
                        self.index = self.path.index((self.x, self.y))
                        self.last_direction = "right"

        # Debugger
        if (self.x, self.y) != self.path[self.index]:
            input(f"INDEX {self.path[self.index]} does not match {(self.x, self.y)}")







    def main(self): # window, fruit, snake, path, maze
        # Starting coordinate for snake

        # Coordinate that cycle starts at# + 1 # Adds to subsititue for starting index at 0
        while True:
            clock = pg.time.Clock()
            clock.tick(0) # Delays frame rate

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            # Redraws fruits

            self.surface.fill(pg.Color(0, 0, 0))
            # Developer tools
            if self.config.hamiltonian_path:    self.hamiltonian_lines()
            if self.config.grid:    self.draw_grid()
            if self.config.maze_lines:  self.prim_lines()

            self.snake.update(self.surface) # Redraws snake
            self.fruit.update(self.surface) # Redraws fruit

            # Decides moves between snake
            self.cheat()
            
            snake.update_movement()

            if self.fruit.collision(snake.head):
                if len(snake.body) < len(self.path):
                    self.score += 1 
                    self.fruit.spawn_fruit()
                    self.snake.extend()
                    pg.display.set_caption(f"Score: {self.score}")
                else:
                    pg.display.set_caption("You Win!")
                    time.sleep(5)
                    pg.quit()
                    sys.exit()
            
            pg.display.update()
            if self.snake.check_collision():
                print(f"Oops! You're dead. Keep debugging. See you in an hour. \n{self.x, self.y}")
                input()
                # time.sleep(3)
                pg.quit()
                sys.exit()

            # input()
            # time.sleep(3)

    def hamiltonian_lines(self):
        for index, coord in enumerate(self.path):
            x, y = coord
            txt = self.font.render(str(index+1), 200, (255, 255, 255), None)
            r = txt.get_rect(center=(CUBE_DIM*x + CUBE_DIM//2, CUBE_DIM*y + CUBE_DIM//2))
            window.blit(txt, r)
            if not index == len(self.path)-1:
                if not index == 0:
                    if self.path[index+1] == (x+1, y) or self.path[index-1] == (x+1, y): # or self.path[index+1] == (x-1, y):
                        pg.draw.line(window, (255, 255, 255), (CUBE_DIM*x + CUBE_DIM*.75, CUBE_DIM*y + CUBE_DIM//2), (CUBE_DIM*(x+1) + CUBE_DIM*.25, CUBE_DIM*y + CUBE_DIM//2))
                    if self.path[index+1] == (x, y+1) or self.path[index-1] == (x, y+1): # or self.path[index+1] == (x, y-1):
                        pg.draw.line(window, (255, 255, 255), (CUBE_DIM*x + CUBE_DIM//2, CUBE_DIM*y + CUBE_DIM*.75), (CUBE_DIM*x + CUBE_DIM//2, CUBE_DIM*(y+1) + CUBE_DIM*.25))
                else:
                    pg.draw.line(window, (255, 255, 255), (CUBE_DIM*x + CUBE_DIM*.75, CUBE_DIM*y + CUBE_DIM//2), (CUBE_DIM*(x+1) + CUBE_DIM*.25, CUBE_DIM*y + CUBE_DIM//2))
                    pg.draw.line(window, (255, 255, 255), (CUBE_DIM*x + CUBE_DIM//2, CUBE_DIM*y + CUBE_DIM*.75), (CUBE_DIM*x + CUBE_DIM//2, CUBE_DIM*(y+1) + CUBE_DIM*.25))
            else:
                pg.draw.line(window, (255, 255, 255), (CUBE_DIM*x + CUBE_DIM//2, CUBE_DIM*y + CUBE_DIM*.75), (CUBE_DIM*x + CUBE_DIM//2, CUBE_DIM*(y+1) + CUBE_DIM*.25))

    def draw_grid(self):
        LINE_COLOR = pg.Color(0, 255, 0)
        for row in range(ROWS): # w600, r400
            row = (row)*CUBE_DIM
            pg.draw.line(window, LINE_COLOR, (0, row), (SCREEN_WIDTH, row), 1)
        for col in range(COLUMNS): # w600, r400
            col = (col)*CUBE_DIM
            pg.draw.line(window, LINE_COLOR, (col, 0), (col, SCREEN_HEIGHT), 1)

    def prim_lines(self):
        MAZE_COLOR = pg.Color(255, 0, 0)
        for key, value in maze.items():
            x, y = key
            x = (x+.5)*CUBE_DIM*2
            y = (y+.5)*CUBE_DIM*2
            x_af = x+CUBE_DIM*2
            y_af = y+CUBE_DIM*2
            for i in value:
                if i == "right":
                    pg.draw.line(window, MAZE_COLOR, (x, y), (x_af, y), 3)
                elif i == "down":
                    pg.draw.line(window, MAZE_COLOR, (x, y), (x, y_af), 3)

    
def prim_maze(maze_rows, maze_columns):
    maze = dict()
    for x in range(maze_columns):
        for y in range(maze_rows):
            maze[x, y] = []
    # Random starting point in maze
    x = randint(0, maze_columns-1)
    y = randint(0, maze_rows-1)
    print(f"x: {x}, y: {y}")
    current_unit = (x, y)
    past_units = [current_unit]
    nearby_units = set()
    while len(past_units) != maze_rows*maze_columns:
        x, y = current_unit

        # Cells not at edges
        if x != 0 and y != 0 and x != maze_columns-1 and y != maze_rows-1:
            nearby_units.add((x, y-1))
            nearby_units.add((x, y+1))
            nearby_units.add((x-1, y))
            nearby_units.add((x+1, y))

        # Cell in top left
        elif x == 0 and y == 0:
            nearby_units.add((x+1, y))
            nearby_units.add((x, y+1))
        
        # Cells in top right
        elif x == maze_columns-1 and y == 0:
            nearby_units.add((x-1, y))
            nearby_units.add((x, y+1))
        
        # Cell in bottom left
        elif y == maze_rows-1 and x == 0:
            nearby_units.add((x+1, y))
            nearby_units.add((x, y-1))
        
        # Cells in bottom right
        elif x == maze_columns-1 and y == maze_rows-1:
            nearby_units.add((x, y-1))
            nearby_units.add((x-1, y))
        
        # Cells in top row
        elif y == 0:
            nearby_units.add((x+1, y))
            nearby_units.add((x-1, y))
            nearby_units.add((x, y+1))

        # Cells in bottom row
        elif y == maze_rows-1:
            nearby_units.add((x, y-1))
            nearby_units.add((x-1, y))
            nearby_units.add((x+1, y))
        
        # Cells in left column
        elif x == 0:
            nearby_units.add((x, y-1))
            nearby_units.add((x, y+1))
            nearby_units.add((x+1, y))
        
        # Cells in right column
        elif x == maze_columns-1:
            nearby_units.add((x, y-1))
            nearby_units.add((x, y+1))
            nearby_units.add((x-1, y))

        while current_unit:
            shuffled_nearby_units = list(nearby_units)
            shuffle(shuffled_nearby_units)
            current_unit = shuffled_nearby_units.pop()
            nearby_units.remove(current_unit)
            # current_unit = (nearby_units.pop())

            if current_unit not in past_units:
                x, y = current_unit
                past_units.append(current_unit)
                # It will place a wall depending on the wall next to it
                if (x+1, y) in past_units:
                    maze[x, y] += ["right"]
                elif (x-1, y) in past_units:
                    maze[x-1, y] += ["right"]
                elif (x, y+1) in past_units:
                    maze[x, y] += ["down"]
                elif (x, y-1) in past_units:
                    maze[x, y-1] += ["down"]
                break
    return maze

def generate_hamiltonian(maze_rows, maze_columns, primsmaze):
    hamiltonian_cycle = dict()
    for x in range(maze_columns*2):
        for y in range(maze_rows*2):
            hamiltonian_cycle[x, y] = []
    
    def check_adjacents(x, y): # Use function for reference
        try:
            if "right" in primsmaze[ox, oy]:
                hamiltonian_cycle[x+1, y] = [(x+2, y)]
                hamiltonian_cycle[x+1, y+1] = [(x+2, y+1)]
            else:
                hamiltonian_cycle[x+1, y] = [(x+1, y+1)]
            if "down" in primsmaze[ox, oy]:
                hamiltonian_cycle[x, y+1] = [x, y+2]
                hamiltonian_cycle[x+1, y+1] = [x+1, y+2]
            else:
                hamiltonian_cycle[x, y+1] = [(x+1, y+1)]
            if "down" not in primsmaze[ox, oy-1]: # Checks if a wall is blocking its right
                hamiltonian_cycle[x, y] = [(x+1, y)]
            if "right" not in primsmaze[ox-1, oy]:
                hamiltonian_cycle[x, y] = [(x, y+1)] # Checks if a wall is blocking underneath
        except:
            pass
    
    for i in range(maze_columns): # x
        for e in range(maze_rows): # y
            ox, oy = (i, e) # Original X and Y
            x, y = (i*2, e*2) # X and Y multiplied for the maze
            # Cells not on an edge
            if ox != maze_columns and oy != maze_rows and ox != 0 and oy != 0:
                if "right" in primsmaze[ox, oy]:
                    hamiltonian_cycle[x+1, y] += [(x+2, y)]
                    hamiltonian_cycle[x+1, y+1] += [(x+2, y+1)]
                else:
                    hamiltonian_cycle[x+1, y] += [(x+1, y+1)]
                if "down" in primsmaze[ox, oy]:
                    hamiltonian_cycle[x, y+1] += [(x, y+2)]
                    hamiltonian_cycle[x+1, y+1] += [(x+1, y+2)]
                else:
                    hamiltonian_cycle[x, y+1] += [(x+1, y+1)]
                if "down" not in primsmaze[ox, oy-1]: # Checks if a wall is blocking its right
                    hamiltonian_cycle[x, y] += [(x+1, y)]
                if "right" not in primsmaze[ox-1, oy]:
                    hamiltonian_cycle[x, y] += [(x, y+1)] # Checks if a wall is blocking underneath
            
            # Cell top left
            elif ox == 0 and oy == 0:
                hamiltonian_cycle[x, y] += [(x+1, y)]
                hamiltonian_cycle[x, y] += [(x, y+1)]
                if "right" in primsmaze[ox, oy]:
                    hamiltonian_cycle[x+1, y] += [(x+2, y)]
                    hamiltonian_cycle[x+1, y+1] += [(x+2, y+1)]
                else:
                    hamiltonian_cycle[x+1, y] += [(x+1, y+1)]
                if "down" in primsmaze[ox, oy]:
                    hamiltonian_cycle[x, y+1] += [(x, y+2)]
                    hamiltonian_cycle[x+1, y+1] += [(x+1, y+2)]
                else:
                    hamiltonian_cycle[x, y+1] += [(x+1, y+1)]

            # Cell top right
            elif oy == 0 and ox == maze_columns-1:
                hamiltonian_cycle[x, y] += [(x+1, y)]
                hamiltonian_cycle[x+1, y] += [(x+1, y+1)]
                if "down" in primsmaze[ox, oy]:
                    hamiltonian_cycle[x, y+1] += [(x, y+2)]
                    hamiltonian_cycle[x+1, y+1] += [(x+1, y+2)]
                else:
                    hamiltonian_cycle[x, y+1] += [(x+1, y+1)]
                if "right" not in primsmaze[ox-1, oy]:
                    hamiltonian_cycle[x, y] += [(x, y+1)] # Checks if a wall is blocking underneath
            
            # Cell bottom right
            elif ox == maze_columns-1 and oy == maze_rows-1:
                hamiltonian_cycle[x+1, y] += [(x+1, y+1)]
                hamiltonian_cycle[x, y+1] += [(x+1, y+1)]
                if "down" not in primsmaze[ox, oy-1]: # Checks if a wall is blocking its right
                    hamiltonian_cycle[x, y] += [(x+1, y)]
                if "right" not in primsmaze[ox-1, oy]:
                    hamiltonian_cycle[x, y] += [(x, y+1)] # Checks if a wall is blocking underneath
                        
            # Cell bottom left
            elif oy == maze_rows-1 and ox == 0:
                hamiltonian_cycle[x, y] += [(x, y+1)]
                hamiltonian_cycle[x, y+1] += [(x+1, y+1)]
                if "right" in primsmaze[ox, oy]:
                    hamiltonian_cycle[x+1, y] += [(x+2, y)]
                    hamiltonian_cycle[x+1, y+1] += [(x+2, y+1)]
                else:
                    hamiltonian_cycle[x+1, y] += [(x+1, y+1)]
                if "down" not in primsmaze[ox, oy-1]: # Checks if a wall is blocking its right
                    hamiltonian_cycle[x, y] += [(x+1, y)]
            
            # Cells top row
            elif oy == 0:
                hamiltonian_cycle[x, y] += [(x+1, y)]
                if "right" in primsmaze[ox, oy]:
                    hamiltonian_cycle[x+1, y] += [(x+2, y)]
                    hamiltonian_cycle[x+1, y+1] += [(x+2, y+1)]
                else:
                    hamiltonian_cycle[x+1, y] += [(x+1, y+1)]
                if "down" in primsmaze[ox, oy]:
                    hamiltonian_cycle[x, y+1] += [(x, y+2)]
                    hamiltonian_cycle[x+1, y+1] += [(x+1, y+2)]
                else:
                    hamiltonian_cycle[x, y+1] += [(x+1, y+1)]
                if "right" not in primsmaze[ox-1, oy]:
                    hamiltonian_cycle[x, y] += [(x, y+1)] # Checks if a wall is blocking underneath
            
            # Cell right column
            elif ox == maze_columns-1:
                hamiltonian_cycle[x+1, y] += [(x+1, y+1)]
                if "down" in primsmaze[ox, oy]:
                    hamiltonian_cycle[x, y+1] += [(x, y+2)]
                    hamiltonian_cycle[x+1, y+1] += [(x+1, y+2)]
                else:
                    hamiltonian_cycle[x, y+1] += [(x+1, y+1)]
                if "down" not in primsmaze[ox, oy-1]: # Checks if a wall is blocking its right
                    hamiltonian_cycle[x, y] += [(x+1, y)]
                if "right" not in primsmaze[ox-1, oy]:
                    hamiltonian_cycle[x, y] += [(x, y+1)] # Checks if a wall is blocking underneath

            # Cells bottom row
            elif oy == maze_rows-1:
                hamiltonian_cycle[x, y+1] += [(x+1, y+1)]
                if "right" in primsmaze[ox, oy]:
                    hamiltonian_cycle[x+1, y] += [(x+2, y)]
                    hamiltonian_cycle[x+1, y+1] += [(x+2, y+1)]
                else:
                    hamiltonian_cycle[x+1, y] += [(x+1, y+1)]
                if "down" not in primsmaze[ox, oy-1]: # Checks if a wall is blocking its right
                    hamiltonian_cycle[x, y] += [(x+1, y)]
                if "right" not in primsmaze[ox-1, oy]:
                    hamiltonian_cycle[x, y] += [(x, y+1)] # Checks if a wall is blocking underneath

            # Cells left column
            elif ox == 0:
                hamiltonian_cycle[x, y] += [(x, y+1)]
                if "right" in primsmaze[ox, oy]:
                    hamiltonian_cycle[x+1, y] += [(x+2, y)]
                    hamiltonian_cycle[x+1, y+1] += [(x+2, y+1)]
                else:
                    hamiltonian_cycle[x+1, y] += [(x+1, y+1)]
                if "down" in primsmaze[ox, oy]:
                    hamiltonian_cycle[x, y+1] += [(x, y+2)]
                    hamiltonian_cycle[x+1, y+1] += [(x+1, y+2)]
                else:
                    hamiltonian_cycle[x, y+1] += [(x+1, y+1)]
                if "down" not in primsmaze[ox, oy-1]: # Checks if a wall is blocking its right
                    hamiltonian_cycle[x, y] += [(x+1, y)]
    return hamiltonian_cycle


def process_cycle(cycle, maze_rows, maze_columns):
    path = [(0, 0)]
    x, y = (0, 0)
    last_dir = None

    while len(path) != maze_rows*2 * maze_columns*2:
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
        else: # Motivation
            print("Go back to 'Hello world' at this point")
            time.sleep(1)
    return path

class DeveloperTools:
    def __init__(self, grid: False, maze_lines: False, hamiltonian_path: False) -> None:
        self.grid = grid
        self.maze_lines = maze_lines
        self.hamiltonian_path = hamiltonian_path








check_measurements()
snake = Snake()
fruit = Fruit(snake)
halfmaze_rows, halfmaze_col = int(SCREEN_HEIGHT/(CUBE_DIM*2)), int(SCREEN_WIDTH/(CUBE_DIM*2))
maze = prim_maze(halfmaze_rows, halfmaze_col)
print("finished prim")
cycle = generate_hamiltonian(halfmaze_rows, halfmaze_col, maze)
print("finished hamiltonian")
path = process_cycle(cycle, halfmaze_rows, halfmaze_col)
# print(path)

pg.init()
window = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
bot = AI(window=window, fruit=fruit, snake=snake, path=path, maze=maze, dev=DeveloperTools(maze_lines=True, hamiltonian_path=True, grid=True), columns=int(SCREEN_WIDTH/(CUBE_DIM)), rows=int(SCREEN_HEIGHT/(CUBE_DIM)))
bot.main() # window, fruit, snake, path, maze
