import pygame
from maze_generators import RandomizedDFS
from drawing_tools import draw_cell
from tools import create_matrix, remove_border, add_all_borders

pygame.init()
clock = pygame.time.Clock()
speed = 60

cell_size = 30
border_size = cell_size // 10 if cell_size // 10 >= 1 else 1

black = (0, 0, 0)
background_color = (150, 150, 150)
cell_color = (200, 200, 200)
curr_cell_color = (50, 150, 50)

cols = rows = 20

surface = pygame.display.set_mode((cell_size * rows, cell_size * cols))

matrix = create_matrix(cols, rows)

curr_cell = prev_cell = matrix[0][0]
add_all_borders(curr_cell)

MazeGenerator = RandomizedDFS((cols, rows))
coord = prev_coord = MazeGenerator.curr

directions = {(0, 1): 'right', (1, 0): 'bottom', (0, -1): 'left', (-1, 0): 'top', (0, 0): None}

get_direction = lambda coord, prev: (prev[0] - coord[0], prev[1] - coord[1])
reverse_direction = lambda coord: (coord[0] * -1, coord[1] * -1)

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

    if MazeGenerator.not_finished and not paused:
        coord = MazeGenerator.move()
        y, x = coord
        curr_cell = matrix[y][x]

        direction = get_direction(coord, prev_coord)
        reversed_direction = reverse_direction(direction)
        direction_name = directions[direction]
        reversed_direction_name = directions[reversed_direction]

        remove_border(curr_cell, direction_name)
        remove_border(prev_cell, reversed_direction_name)

        prev_coord = coord
        prev_cell = curr_cell

    for y, row in enumerate(matrix):
        for x, cell in enumerate(row):
            pos = (y, x)
            if pos in MazeGenerator.visited:  # Draw cell only if it was already visited
                draw_cell(surface, pos, cell, cell_size, cell_color, border_size=border_size)

    draw_cell(surface, coord, curr_cell, cell_size, curr_cell_color, border_size)  # Highlight current cell

    clock.tick(speed)
    pygame.display.flip()
