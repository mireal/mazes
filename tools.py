class Cell:
    def __init__(self, top=1, bottom=1, left=1, right=1):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right


directions = {(0, 1): 'right', (1, 0): 'bottom', (0, -1): 'left', (-1, 0): 'top', (0, 0): None}


def remove_all_borders(cell: Cell):
    cell.top = 0
    cell.bottom = 0
    cell.left = 0
    cell.right = 0


def add_all_borders(cell: Cell):
    cell.top = 1
    cell.bottom = 1
    cell.left = 1
    cell.right = 1


def add_border(cell: Cell, direction: str):
    if direction == 'top':
        cell.top = 1
    if direction == 'bottom':
        cell.bottom = 1
    if direction == 'left':
        cell.left = 1
    if direction == 'right':
        cell.right = 1


def remove_border(cell: Cell, direction: str):
    if direction == 'top':
        cell.top = 0
    if direction == 'bottom':
        cell.bottom = 0
    if direction == 'left':
        cell.left = 0
    if direction == 'right':
        cell.right = 0


def add_tuple(t1: tuple, t2: tuple) -> tuple:
    y = t1[0] + t2[0]
    x = t1[1] + t2[1]
    return y, x


def get_direction(pos: tuple, prev_pos: tuple) -> tuple:
    y = prev_pos[0] - pos[0]
    x = prev_pos[1] - pos[1]
    return y, x


def reverse_direction(pos: tuple) -> tuple:
    y = pos[0] * -1
    x = pos[1] * -1
    return y, x


def manhattan_distance(start: tuple, end: tuple) -> int:
    y1, x1 = start
    y2, x2 = end
    dist = abs(x1 - x2) + abs(y1 - y2)
    return dist


def create_empty_maze(cols: int, rows: int) -> list[list]:
    matrix = []
    for y in range(cols):
        row = []
        for x in range(rows):
            cell = Cell()
            row.append(cell)
        matrix.append(row)
    return matrix


def deep_copy(matrix: list[list]) -> list[list]:
    new_matrix = []
    cols, rows = len(matrix), len(matrix[0])
    for y in range(cols):
        row = []
        for x in range(rows):
            cell = matrix[y][x]
            args = cell.__dict__
            new_cell = Cell(top=args['top'], bottom=args['bottom'], left=args['left'], right=args['right'])
            row.append(new_cell)
        new_matrix.append(row)
    return new_matrix


if __name__ == '__main__':
    rows, cols = 3, 3
    maze = create_empty_maze(cols, rows)
    maze_copy = deep_copy(maze)

    cell = maze[0][0]
    cell_copy = maze_copy[0][0]
    print(cell.__dict__ == cell_copy.__dict__)
    print(cell == cell_copy)
