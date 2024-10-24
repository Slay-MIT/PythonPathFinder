import pygame
import math
from queue import PriorityQueue

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path-Finding Algorithm")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)
PINK_RED = (255, 0, 128)
YELLOW = (247, 240, 27)
LIGHT_PURPLE = (188, 116, 247)

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row*width
        self.y = col*width
        self.color = WHITE
        self.width = width
        self.total_rows = total_rows
    
    def get_pos(self):
        return self.row, self.col
    
    def is_closed(self):
        return self.color==PINK_RED
    
    def is_open(self):
        return self.color==GREEN
    
    def is_barrier(self):
        return self.color==BLACK
    
    def is_start(self):
        return self.color==YELLOW
    
    def is_end(self):
        return self.color==TURQUOISE
    
    def reset(self):
        self.color=WHITE
    
    def make_start(self):
        self.color = YELLOW

    def make_closed(self):
        self.color = PINK_RED

    def make_open(self):
        self.color = GREEN;
    
    def make_barrier(self):
        self.color = BLACK
    
    def make_end(self):
        self.color = TURQUOISE
    
    def make_path(self):
        self.color = PURPLE
    
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))
    
    def update_neighbors(self, grid):
        
        self.neighbors = []

        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): #moving DOWN a row
            self.neighbors.append(grid[self.row + 1][self.col])
            
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): #moving UP a row
            self.neighbors.append(grid[self.row - 1][self.col])
        
        if self.col < self.total_rows - 1 and not grid[self.row][self.col+1].is_barrier(): #moving RIGHT a row
            self.neighbors.append(grid[self.row][self.col+1])
        
        if self.col > 0 and not grid[self.row][self.col-1].is_barrier(): #moving LEFT a row
            self.neighbors.append(grid[self.row][self.col-1])

    
    def __lt__(self, other):
        return False
    
#Heuristic Function
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1-x2)+abs(y1-y2) #Manhattan Distance

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {node: float("inf") for row in grid for node in row} #dictionary comprehension
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row} #dictionary comprehension
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start} #A set to store elements so that duplicates are not stored
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #To exit the while loop
                pygame.quit()
        current = open_set.get()[2] #to get the lowest value F-score; we do [2] to get just the node (look at the open_set parameters)
        open_set_hash.remove(current)

        if current == end: #when we reach the destination
            reconstruct_path(came_from, end, draw)
            end.make_end()
            start.make_start()
            return True
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1 #we add 1 cuz we are going one node over ?

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count+=1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
        draw()
        if current != start:
            current.make_closed()
    return False



#Making the grid to hold the nodes
def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid

#To Draw the Grid
def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, BLACK, (0, i*gap), (width, i*gap))
        for j in range(rows):
            pygame.draw.line(win, BLACK, (j * gap, 0), (j*gap, width))

#The Draw Function
def draw(win, grid, rows, width):
    win.fill(BLACK)
    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()

def get_clicked_position(pos, rows, width):
    gap = width//rows
    y,x = pos
    row = y // gap
    col = x // gap

    return row, col

def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)
    start = None
    end = None
    running = True
    started = False
    
    while running:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                running = False
            #Started so that once the algorithm has started the user is not able to change obstacles (only press the cross button) as it can mess things up
            if pygame.mouse.get_pressed()[0]: #0 stands for LEFT mouse button
                pos = pygame.mouse.get_pos()
                row ,col = get_clicked_position(pos, ROWS, width)
                node = grid[row][col]
                if not start and node!=end:
                    start = node
                    start.make_start()
                elif not end and node!=start:
                    end = node
                    end.make_end()
                elif node != end and node != start:
                    node.make_barrier()
            elif pygame.mouse.get_pressed()[2]: #2 stands for RIGHT mouse button; 1 stands for middle button
                pos = pygame.mouse.get_pos()
                row ,col = get_clicked_position(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node==start:
                    start=None
                elif node==end:
                    end=None
            if event.type==pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    algorithm(lambda: draw(win, grid, ROWS, width), grid , start, end)
    
                if event.key==pygame.K_c: #To clear/rest the grid, press c
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)
    #To stop the program
    pygame.quit()

main(WIN, WIDTH)

