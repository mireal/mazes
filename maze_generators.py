from random import choice


class RandomizedDFS:
    def __init__(self, grid_size: tuple, start_coord: tuple = (0, 0)):
        self.col_len, self.row_len = grid_size
        self.max_size = self.col_len * self.row_len
        self.curr = start_coord
        self.not_finished = True
        self.visited = set()
        self.visited.add(start_coord)
        self.stack = []

        self.add_tuple = lambda coord, move: (coord[0] + move[0], coord[1] + move[1])

    def move(self):
        if len(self.visited) == self.max_size:
            self.not_finished = False
            return self.curr

        available_moves = self.possible_moves()
        if available_moves:
            move = choice(available_moves)
            self.curr = self.add_tuple(self.curr, move)
            self.visited.add(self.curr)
            self.stack.append(self.curr)
        else:
            self.stack.pop()
            self.curr = self.stack[-1]

        return self.curr

    def possible_moves(self):
        moves = []
        for move in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            y, x = self.curr
            move_y, move_x = move
            y += move_y
            x += move_x
            if (y, x) not in self.visited and 0 <= y < self.col_len and 0 <= x < self.row_len:
                moves.append(move)

        return moves


if __name__ == '__main__':
    from time import sleep

    len_y, len_x = 20, 20
    board = [['.' for _ in range(len_x)] for _ in range(len_y)]
    board_size = (len_y, len_x)
    coord = (0, 0)
    dfs = RandomizedDFS(board_size, coord)


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


    for i in range(1000):
        dfs = RandomizedDFS((1, i + 2), coord)
        while dfs.not_finished:
            dfs.move()
        print(f'{i + 1} successfully finished')

    print('Done')
