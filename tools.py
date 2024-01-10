class Cell:
    def __init__(self, top=1, bottom=1, left=1, right=1):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right


def remove_all_borders(cell):
    cell.top = 0
    cell.bottom = 0
    cell.left = 0
    cell.right = 0


def add_all_borders(cell):
    cell.top = 1
    cell.bottom = 1
    cell.left = 1
    cell.right = 1


def add_border(cell, direction):
    if direction == 'top':
        cell.top = 1
    if direction == 'bottom':
        cell.bottom = 1
    if direction == 'left':
        cell.left = 1
    if direction == 'right':
        cell.right = 1


def remove_border(cell, direction):
    if direction == 'top':
        cell.top = 0
    if direction == 'bottom':
        cell.bottom = 0
    if direction == 'left':
        cell.left = 0
    if direction == 'right':
        cell.right = 0


def create_empty_maze(cols: int, rows: int):
    matrix = []
    for y in range(cols):
        row = []
        for x in range(rows):
            cell = Cell()
            row.append(cell)
        matrix.append(row)
    return matrix


def deep_copy(matrix: list[list]):
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
