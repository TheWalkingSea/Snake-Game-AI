import pygame as pg
from random import randint, shuffle
from collections import deque
import sys
import os
import time



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

    pass
class Fruit:

    def __init__(self, snake: "Snake") -> None:
        self.color = pg.Color(231, 76, 27) # Default color for Google Snake
        self.unitsize  = CUBE_DIM # Defines the dimensions of the cube
        # Initial position for fruit
        # self.x = randint(0, int(SCREEN_WIDTH / self.unitsize - 1)) * self.unitsize
        # self.y = randint(0, int(SCREEN_HEIGHT / self.unitsize - 1)) * self.unitsize
        self.x, self.y = (560, 240)
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
        self.head = pg.Rect(self.x, self.y, self.unitsize, self.unitsize)
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
            print(self.head.colliderect(unit))
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

def hamiltonian_lines(window, cycle, font):
    for index, coord in enumerate(cycle):
        x, y = coord
        txt = font.render(str(index+1), 200, (255, 255, 255), None)
        r = txt.get_rect(center=(CUBE_DIM*x + CUBE_DIM//2, CUBE_DIM*y + CUBE_DIM//2))
        window.blit(txt, r)
        if not index == len(cycle)-1:
            if not index == 0:
                if cycle[index+1] == (x+1, y) or cycle[index-1] == (x+1, y): # or cycle[index+1] == (x-1, y):
                    pg.draw.line(window, (255, 255, 255), (CUBE_DIM*x + CUBE_DIM*.75, CUBE_DIM*y + CUBE_DIM//2), (CUBE_DIM*(x+1) + CUBE_DIM*.25, CUBE_DIM*y + CUBE_DIM//2))
                if cycle[index+1] == (x, y+1) or cycle[index-1] == (x, y+1): # or cycle[index+1] == (x, y-1):
                    pg.draw.line(window, (255, 255, 255), (CUBE_DIM*x + CUBE_DIM//2, CUBE_DIM*y + CUBE_DIM*.75), (CUBE_DIM*x + CUBE_DIM//2, CUBE_DIM*(y+1) + CUBE_DIM*.25))
            else:
                pg.draw.line(window, (255, 255, 255), (CUBE_DIM*x + CUBE_DIM*.75, CUBE_DIM*y + CUBE_DIM//2), (CUBE_DIM*(x+1) + CUBE_DIM*.25, CUBE_DIM*y + CUBE_DIM//2))
                pg.draw.line(window, (255, 255, 255), (CUBE_DIM*x + CUBE_DIM//2, CUBE_DIM*y + CUBE_DIM*.75), (CUBE_DIM*x + CUBE_DIM//2, CUBE_DIM*(y+1) + CUBE_DIM*.25))
        else:
            pg.draw.line(window, (255, 255, 255), (CUBE_DIM*x + CUBE_DIM//2, CUBE_DIM*y + CUBE_DIM*.75), (CUBE_DIM*x + CUBE_DIM//2, CUBE_DIM*(y+1) + CUBE_DIM*.25))


def prim_lines(window, maze):
    LINE_COLOR = pg.Color(0, 255, 0)
    MAZE_COLOR = pg.Color(255, 0, 0)
    for row in range(ROWS): # w600, r400
        row = (row)*CUBE_DIM
        pg.draw.line(window, LINE_COLOR, (0, row), (SCREEN_WIDTH, row), 1)
    for col in range(COLUMNS): # w600, r400
        col = (col)*CUBE_DIM
        pg.draw.line(window, LINE_COLOR, (col, 0), (col, SCREEN_HEIGHT), 1)

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




def check_hamiltonicity(coord: "tuple", path, body) -> "bool":
    x, y = coord # new head coordinates
    body.pop() # Remove tail
    body = deque(body).appendleft((coord)) # Add head to simulate temporary movement
    for unit in body: # Body is already parsed
        path.remove(body)
    while (flag := True):
        if (x+1, y) not in body:
            break


def cheat(fruit: "Fruit", snake: "Snake", path, last_dir, ox, oy, oindex):
    if snake.body: body = list(map(lambda x: (x[0]//CUBE_DIM, x[1]//CUBE_DIM), snake.body))
    else: body = snake.body # Empty List

    fx, fy = (fruit.x//CUBE_DIM, fruit.y//CUBE_DIM)
    sx, sy = (snake.x//CUBE_DIM, snake.y//CUBE_DIM)
    findex = path.index((fx, fy))
    sindex = path.index((sx, sy))
    try:
        pathtofruit = path[sindex:findex+1]
        pathtofruit.pop(1)
    except IndexError: # Errors when it has to cycle the entire hamiltonian cycle again
        try:
            # pathtofruit = path[findex:sindex+1]
            pathtofruit = path[sindex:] + path[:findex+1]
            # pathtofruit.reverse()
            pathtofruit.pop(1)
            # input("PATHHH")
            # return path, False, ox, oy, oindex
        except IndexError: print("+1 Point. Yummy!")
    potential_cheats = dict() # Coords: index

    x, y = pathtofruit[0]
    if (x-1, y) in pathtofruit and (x-1, y) not in body and last_dir != "right" and x != COLUMNS-1: # Left Cheat
        endindex = pathtofruit.index((x-1, y))
        potential_cheats[pathtofruit.index((x-1, y))] = [pathtofruit[endindex], "left", *(x-1, y)] # , path.index((x-1, y))]
        print(f"left {x, y}")

    if (x+1, y) in pathtofruit and (x+1, y) not in body and last_dir != "left" and x != 0: # Right Cheat
        endindex = pathtofruit.index((x+1, y))
        potential_cheats[pathtofruit.index((x+1, y))] = [pathtofruit[endindex], "right", *(x+1, y)] # , path.index((x+1, y))]
        print(f"right {x, y}")

    if (x, y-1) in pathtofruit and (x, y-1) not in body and last_dir != "down" and y != 0: # Up Cheat
        endindex = pathtofruit.index((x, y-1))
        potential_cheats[pathtofruit.index((x, y-1))] = [pathtofruit[endindex], "up", *(x, y-1)] # , path.index((x, y-1))]
        print(f"up {x, y}")

    if (x, y+1) in pathtofruit and (x, y+1) not in body and last_dir != "up" and y != ROWS-1: # Down Cheat
        endindex = pathtofruit.index((x, y+1))
        potential_cheats[pathtofruit.index((x, y+1))] = [pathtofruit[endindex], "down", *(x, y+1)] # , path.index((x, y+1))]
        print(f"down {x, y}")

    if potential_cheats and (snake.head[0], snake.head[1]) != (fruit.x, fruit.y):
        print("Cheating")
        best_index = max(potential_cheats.keys())
        best_coord, last_dir, xxx, xxy = potential_cheats[best_index]
        ox, oy = pathtofruit[best_index]
        # print(index, "\n\n", best_coord, index)
        # newpath = path[:path.index((sx, sy))] + path[path.index(best_coord):]
        newpath = [None]
        print(len(path) - len(newpath) - 1)
        print(f"NEW INDEX: {len(path) - abs(len(newpath)) - 1 + oindex}")
        print(f"NEW COORD: {sx, sy} --> {ox, oy} UNDER")
        snake.change_dir(last_dir)
        return newpath, True, *best_coord, path.index((ox, oy)), last_dir # len(path) - len(newpath) - 1 + oindex
        
    else:
        print("No cheats")
        return path, False, ox, oy, oindex, last_dir







def main(window, fruit: "Fruit", snake: "Snake", path, maze):
    # Starting coordinate for snake
    pos = (int(snake.x/CUBE_DIM), int(snake.y/CUBE_DIM))
    x, y = pos
    font = pg.font.SysFont("arial", 12)

    last_dir = None
    # Coordinate that cycle starts at
    index = path.index(pos)# + 1 # Adds to subsititue for starting index at 0
    score = 1
    while True:
        clock = pg.time.Clock()
        clock.tick(0) # Delays frame rate

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        # Redraws fruits

        window.fill(pg.Color(0, 0, 0))
        hamiltonian_lines(window, path, font)
        snake.update(window)
        fruit.update(window)
        prim_lines(window, maze)
        print(f"before index {index}")
        newpath, ifcheated, x, y, index, last_dir = cheat(fruit, snake, path, last_dir, x, y, index)
        # newpath, ifcheated = path, False
        # Changes direction
        if index+1 < len(path) and not ifcheated:
            print("Running default hamiltonian cycle")
            if snake.body: body = list(map(lambda x: (x[0]//CUBE_DIM, x[1]//CUBE_DIM), snake.body))
            else: body = snake.body # Empty List

            if path[index+1] == (x, y+1) and last_dir != "up" and (x, y+1) not in body:
                snake.change_dir("down")
                x, y = (x, y+1)
                last_dir = "down"
            elif path[index+1] == (x, y-1) and last_dir != "down" and (x, y-1) not in body:
                snake.change_dir("up")
                x, y = (x, y-1)
                last_dir = "up"
            elif path[index+1] == (x-1, y) and last_dir != "right" and (x-1, y) not in body:
                snake.change_dir("left")
                x, y = (x-1, y)
                last_dir = "left"
            elif path[index+1] == (x+1, y) and last_dir != "left" and (x+1, y) not in body:
                snake.change_dir("right")
                x, y = (x+1, y)
                last_dir = "right"
            else:
                print(f"{(x, y)} --> {path[index+1]}")
                print("You suck at programming, go back to Scratch")
                print(f"LAST DIR: {last_dir}")
                time.sleep(1)
                pg.display.update()
                input()
        print(f"LAST DIR: {last_dir}")
        #  Special case when list ends and is stuck at (0, 1)
        if index+1 == len(path) and not ifcheated:
            snake.change_dir("up")
            last_dir = "up"
            x, y = (x, y-1)
            index = 0
        elif not ifcheated:
            index += 1
        
        snake.update_movement()

        if fruit.collision(snake.head):
            if len(snake.body) < len(path):
                score += 1
                fruit.spawn_fruit()
                snake.extend()
                pg.display.set_caption(f"Score: {score}")
            else:
                pg.display.set_caption("You Win!")
                time.sleep(5)
                pg.quit()
                sys.exit()
        

        if snake.check_collision():
            print("dead :p")
            pg.display.update()
            input()
            # time.sleep(3)
            pg.quit()
            sys.exit()   
        pg.display.update()
        print("\n\n\n")
        # input()
        # time.sleep(3)
    
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
pg.font.init()
window = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
main(window, fruit, snake, path, maze)







                



                    
