from random import choice, randint, shuffle
from tools import add_tuple, get_direction, reverse_tuple, directions, remove_border

class PlaceholderGenerator:
    def __init__(self, grid_size: tuple, start_coord: tuple = (0, 0)):
        self.col_len, self.row_len = grid_size
        self.curr = self.prev = start_coord
        self.not_finished= False

class HuntAndKill:
    def __init__(self, grid_size: tuple, start_coord: tuple = (0, 0)):
        self.col_len, self.row_len = grid_size
        self.max_size = self.col_len * self.row_len
        self.curr = self.prev = start_coord
        self.hunter_curr = start_coord
        self.not_finished = True
        self.visited = set()
        self.visited.add(start_coord)
        self.hunt_mode = False

    def move(self):
        if self.hunt_mode:
            pos = self.hunt()
            self.hunter_curr = pos
            if pos not in self.visited and self.not_finished:
                self.curr = pos
                self.prev = self.find_passage()
                self.visited.add(pos)
                self.hunt_mode = False
        else:
            move = self.kill()
            if not move:
                self.hunt_mode = True
            else:
                self.visited.add(move)
                self.prev = self.curr
                self.curr = move

        return self.curr

    def hunt(self):
        y, x = self.hunter_curr
        x += 1
        if x >= self.row_len:
            x = 0
            y += 1
            if y >= self.col_len:
                self.not_finished = False
                return

        return (y, x)


    def kill(self):
        moves = []
        for move in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            next_move = add_tuple(self.curr, move)
            y, x = next_move
            if next_move not in self.visited and 0 <= y < self.col_len and 0 <= x < self.row_len:
                moves.append(next_move)
        if not moves:
            return
        shuffle(moves)
        return moves[0]

    def find_passage(self):
        moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        shuffle(moves)
        for move in moves:
            passage = add_tuple(self.curr, move)
            y, x = passage
            if passage in self.visited and 0 <= y < self.col_len and 0 <= x < self.row_len:
                return passage

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
        possible_moves = self.possible_moves()
        self.prev = self.curr
        if possible_moves:
            move = choice(possible_moves)
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
    def __init__(self, grid_size: tuple, start_coord: tuple = (0, 0), start_at_random=False, start_at_center=True):
        self.col_len, self.row_len = grid_size
        self.max_size = self.col_len * self.row_len
        self.curr = self.prev = start_coord
        if start_at_random:
            y, x = randint(0, self.col_len - 1), randint(0, self.row_len - 1)
            self.curr = (y, x)
        elif start_at_center:
            y, x = self.col_len // 2, self.row_len // 2
            self.curr = (y, x)
        self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self.not_finished = True
        self.visited = set()
        self.visited.add(self.curr)
        self.frontiers = set()
        self.find_frontiers()

    def move(self):
        self.curr = choice(tuple(self.frontiers))
        self.frontiers.remove(self.curr)
        self.find_frontiers()
        self.visited.add(self.curr)
        passage = self.find_passage()
        self.prev = passage
        if not self.frontiers or len(self.visited) == self.max_size:
            self.not_finished = False
        return self.curr

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
    while generator.not_finished and not paused:
        coord = generator.move()
        prev_coord = generator.prev

        y, x = coord
        prev_y, prev_x = prev_coord

        curr_cell = maze[y][x]
        prev_cell = maze[prev_y][prev_x]

        direction = get_direction(coord, prev_coord)
        reversed_direction = reverse_tuple(direction)

        direction_name = directions[direction]
        reversed_direction_name = directions[reversed_direction]

        remove_border(curr_cell, direction_name)
        remove_border(prev_cell, reversed_direction_name)

        if step_by_step:
            break


if __name__ == '__main__':
    from time import sleep
    from tools import create_empty_maze
    from maze_solvers import DFS
    cols, rows = 20, 20

    size = (cols, rows)
    for i in range(10):
        generator = HuntAndKill(size)
        maze = create_empty_maze(cols, rows)

        while generator.not_finished:
            maze_filler(maze,generator,step_by_step=True)

        solver = DFS(maze)

        while solver.not_finished:
            if not solver.queue:
                print(f'Generation {i + 1}: Not solvable')
                break
            solver.move()
        else:
            print(f'Generation {i + 1}: Solved')