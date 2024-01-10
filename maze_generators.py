from random import choice, randint, shuffle

add_tuple = lambda coord, move: (coord[0] + move[0], coord[1] + move[1])


class RandomizedDFS:
    def __init__(self, grid_size: tuple, start_coord: tuple = (0, 0)):
        self.col_len, self.row_len = grid_size
        self.max_size = self.col_len * self.row_len
        self.curr = self.prev = start_coord
        self.not_finished = True
        self.visited = set()
        self.visited.add(start_coord)
        self.stack = []

    def move(self):
        available_moves = self.possible_moves()
        self.prev = self.curr
        if available_moves:
            move = choice(available_moves)
            self.curr = add_tuple(self.curr, move)
            self.visited.add(self.curr)
            self.stack.append(self.curr)
        else:
            self.stack.pop()
            self.curr = self.stack[-1]

        if len(self.visited) == self.max_size:
            self.not_finished = False

        return self.curr

    def possible_moves(self):
        moves = []
        for move in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            next_move = add_tuple(self.curr, move)
            y, x = next_move
            if next_move not in self.visited and 0 <= y < self.col_len and 0 <= x < self.row_len:
                moves.append(move)

        return moves


class RandomizedPrim:
    def __init__(self, grid_size: tuple, start_coord: tuple = (0, 0), start_at_random=True):
        self.col_len, self.row_len = grid_size
        self.max_size = self.col_len * self.row_len
        self.curr = self.prev = start_coord
        if start_at_random:
            y, x = randint(0, self.col_len - 1), randint(0, self.row_len - 1)
            self.curr = (y, x)
        self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self.not_finished = True
        self.visited = set()
        self.visited.add(self.curr)
        self.frontiers = set()
        self.find_frontiers()

    def move(self):
        self.prev = self.curr
        self.curr = choice(tuple(self.frontiers))
        self.frontiers.remove(self.curr)
        self.find_frontiers()
        self.visited.add(self.curr)
        passage = self.find_passage()
        if not self.frontiers or len(self.visited) == self.max_size:
            self.not_finished = False
        return passage

    def find_frontiers(self):
        for direction in self.directions:
            frontier = add_tuple(self.curr, direction)
            y, x = frontier
            if frontier not in self.visited and 0 <= y < self.col_len and 0 <= x < self.row_len:
                self.frontiers.add(frontier)

    def find_passage(self):
        shuffle(self.directions)
        for direction in self.directions:
            passage = add_tuple(self.curr, direction)
            if passage in self.visited:
                return passage


def maze_filler(maze, generator, step_by_step=False, paused=False):
    from tools import remove_border

    directions = {(0, 1): 'right', (1, 0): 'bottom', (0, -1): 'left', (-1, 0): 'top', (0, 0): None}

    get_direction = lambda coord, prev: (prev[0] - coord[0], prev[1] - coord[1])
    reverse_direction = lambda coord: (coord[0] * -1, coord[1] * -1)

    while generator.not_finished and not paused:
        if type(generator) == RandomizedDFS:
            coord = generator.move()
            prev_coord = generator.prev

        elif type(generator) == RandomizedPrim:
            prev_coord = generator.move()
            coord = generator.curr

        y, x = coord
        prev_y, prev_x = prev_coord

        curr_cell = maze[y][x]
        prev_cell = maze[prev_y][prev_x]

        direction = get_direction(coord, prev_coord)
        reversed_direction = reverse_direction(direction)
        direction_name = directions[direction]
        reversed_direction_name = directions[reversed_direction]

        remove_border(curr_cell, direction_name)
        remove_border(prev_cell, reversed_direction_name)

        if step_by_step:
            break


if __name__ == '__main__':
    from time import sleep

    len_y, len_x = 20, 20
    board = [['.' for _ in range(len_x)] for _ in range(len_y)]
    board_size = (len_y, len_x)
    coord = (0, 0)
    dfs = RandomizedDFS(board_size, coord)
    prim = RandomizedPrim(board_size)


    def draw_board(board):
        for row in board:
            for i, ch in enumerate(row):
                if i != len(row) - 1:
                    print(f' {ch}', end='')
                else:
                    print(f' {ch}')
        print(' ')


    def deep_copy(board: list[list]):
        new_board = []
        for row in board:
            new_row = []
            for ch in row:
                new_row.append(ch)
            new_board.append(new_row)
        return new_board


    def draw_maze(speed):
        while dfs.not_finished:
            y, x = dfs.move()
            board[y][x] = '*'
            curr_board = deep_copy(board)
            # noinspection PyTypeChecker
            curr_board[y][x] = 'X'
            draw_board(curr_board)
            sleep(speed)


    for x in range(100):
        while prim.not_finished:
            coord = prim.move()
            if type(coord) != tuple:
                print(coord)

    print('Done')
