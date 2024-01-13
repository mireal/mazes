import pygame


def draw_cell(surface: pygame.Surface, coord: tuple, cell, size: int, color: tuple, border_size: int,
              offsets: tuple = (0, 0),
              border_color: tuple = (0, 0, 0)):

    y, x = coord
    y_offset, x_offset = offsets

    rect_left = x * size + x_offset
    rect_top = y * size + y_offset
    rect = pygame.Rect(rect_left, rect_top, size, size)

    borders = cell.__dict__

    top_left = (rect_left, rect_top)
    top_right = (rect_left + size, rect_top)
    bottom_left = (rect_left, rect_top + size)
    bottom_right = (rect_left + size, rect_top + size)

    pygame.draw.rect(surface, color, rect)
    if borders['top']:
        pygame.draw.line(surface, border_color, top_left, top_right, border_size)
    if borders['right']:
        pygame.draw.line(surface, border_color, top_right, bottom_right, border_size)
    if borders['bottom']:
        pygame.draw.line(surface, border_color, bottom_left, bottom_right, border_size)
    if borders['left']:
        pygame.draw.line(surface, border_color, top_left, bottom_left, border_size)


def draw_board(surface: pygame.Surface, board: list[list], size: int, color: tuple, border_size: int,
               offsets: tuple = (0, 0),
               border_color: tuple = (0, 0, 0)):
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            coord = (y, x)
            draw_cell(surface, coord, cell, size, color, border_size, offsets=offsets,
                      border_color=border_color)


if __name__ == '__main__':
    pass
