import pygame
from maze_generators import RandomizedDFS
from pygame_cell import Cell

pygame.init()
clock = pygame.time.Clock()
speed = 30

cell_size = 10
border_size = cell_size // 10 if cell_size // 10 >= 1 else 1

black = (0, 0, 0)
background_color = (150, 150, 150)
cell_color = (200, 200, 200)
curr_cell_color = (50, 150, 50)

cols = rows = 100
surface = pygame.display.set_mode((cell_size * cols, cell_size * rows))

MazeGenerator = RandomizedDFS((cols, rows))
coord = prev_coord = MazeGenerator.curr
cells = {}
CurrCell = PrevCell = Cell(surface, coord, size=cell_size, border_size=border_size)
cells[coord] = CurrCell

directions = {(0, 1): 'right', (1, 0): 'bottom', (0, -1): 'left', (-1, 0): 'top'}

substract_tuple = lambda coord, prev: (prev[0] - coord[0], prev[1] - coord[1])
reverse_tuple = lambda coord: (coord[0] * -1, coord[1] * -1)

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

    if MazeGenerator.not_finished and not paused:
        coord = MazeGenerator.move()

        if coord not in cells:
            CurrCell = Cell(surface, coord, size=cell_size, border_size=border_size)
            cells[coord] = CurrCell

            direction = substract_tuple(coord, prev_coord)
            reversed_direction = reverse_tuple(direction)

            dir_name = directions[direction]
            prev_dir_name = directions[reversed_direction]

            CurrCell.borders[dir_name] = 0
            PrevCell.borders[prev_dir_name] = 0

        else:
            CurrCell = cells[coord]

        PrevCell.color = cell_color
        CurrCell.color = curr_cell_color

        prev_coord = coord
        PrevCell = CurrCell

    for cell in cells.values():
        cell.draw_cell()

    clock.tick(speed)
    pygame.display.flip()
