import pygame

cell_size = 5
cell_color = (200, 200, 200)


class Cell:
    def __init__(self, surface: pygame.Surface, coord: tuple, offsets: tuple = (0, 0),
                 size: int = cell_size, color: tuple = cell_color, border_size: int = 1,
                 border_color: tuple = (0, 0, 0)):
        self.surface = surface
        self.color = color
        self.y, self.x = coord

        y_offset, x_offset = offsets
        rect_left = self.x * size + x_offset
        rect_top = self.y * size + y_offset
        self.rect = pygame.Rect(rect_left, rect_top, size, size)

        self.borders = {'top': 1, 'right': 1, 'bottom': 1, 'left': 1}
        self.border_size = border_size
        self.border_color = border_color
        self.top_left = (rect_left, rect_top)
        self.top_right = (rect_left + size, rect_top)
        self.bottom_left = (rect_left, rect_top + size)
        self.bottom_right = (rect_left + size, rect_top + size)

    def draw_cell(self):
        pygame.draw.rect(self.surface, self.color, self.rect)
        self.draw_borders()

    def draw_borders(self):
        if self.borders['top']:
            pygame.draw.line(self.surface, self.border_color, self.top_left, self.top_right, self.border_size)
        if self.borders['right']:
            pygame.draw.line(self.surface, self.border_color, self.top_right, self.bottom_right, self.border_size)
        if self.borders['bottom']:
            pygame.draw.line(self.surface, self.border_color, self.bottom_left, self.bottom_right, self.border_size)
        if self.borders['left']:
            pygame.draw.line(self.surface, self.border_color, self.top_left, self.bottom_left, self.border_size)


if __name__ == '__main__':
    pygame.init()
    clock = pygame.time.Clock()
    surface = pygame.display.set_mode((500, 500))
    running = True

    cell = Cell(surface, (1, 1), (0, 0), size=200, border_size=10)
    while running:
        surface.fill((100, 100, 100))
        cell.draw_cell()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        clock.tick(1)
        pygame.display.flip()
