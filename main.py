import pygame
from maze_generators import RandomizedDFS, RandomizedPrim, maze_filler
from maze_solvers import DFS
from drawing_tools import draw_cell
from tools import create_empty_maze

pygame.init()
clock = pygame.time.Clock()
speed = 30

cols = rows = 20
cell_size = 30
border_size = cell_size // 10 if cell_size // 10 >= 1 else 1

surface = pygame.display.set_mode((cell_size * rows, cell_size * cols))
pygame.display.set_caption('Maze algorithms')

black = (0, 0, 0)
background_color = (150, 150, 150)
cell_color = (200, 200, 200)
visited_cell_color = (150, 100, 100)

generator_cell_color = (50, 150, 50)

maze = create_empty_maze(cols, rows)

# generator = RandomizedDFS((cols, rows))
generator = RandomizedPrim((cols, rows))
solver = None

running = True
paused = True

while running:
    surface.fill(background_color)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_ESCAPE:
                running = False

    maze_filler(maze, generator, step_by_step=True, paused=paused)

    if generator.not_finished == False and solver == None:
        solver = DFS(maze)

    if solver and solver.not_finished and not paused:
        solver.move()

    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            pos = (y, x)
            if solver:
                if pos in solver.visited:
                    color = visited_cell_color
                else:
                    color = cell_color
                draw_cell(surface, pos, cell, cell_size, color, border_size=border_size)
            elif pos in generator.visited:  # Draw cell only if it was already visited
                draw_cell(surface, pos, cell, cell_size, cell_color, border_size=border_size)
    if generator.not_finished:
        pos = generator.curr
        front_cell_color = generator_cell_color
    if solver:
        pos = solver.curr
        front_cell_color = visited_cell_color

    y, x = pos
    cell = maze[y][x]
    draw_cell(surface, pos, cell, cell_size, front_cell_color, border_size)  # Highlight current cell

    clock.tick(speed)
    pygame.display.flip()
