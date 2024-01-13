from tools import add_tuple, directions


class DFS:
    def __init__(self, maze: list[list], start: tuple = (0, 0), end: tuple = None, manhattan_distance=True):
        self.direction_names = directions
        self.use_manhattan_distance = manhattan_distance
        self.not_finished = True
        self.maze = maze
        self.cols, self.rows = len(maze), len(maze[0])
        self.start = start
        self.end = (self.cols - 1, self.rows - 1)
        if end:
            self.end = end
        self.curr = start
        self.visited = set()
        self.visited.add(start)
        self.queue = []
        self.queue.extend(self.find_passages())

    def move(self):
        self.curr = self.queue.pop()
        passages = self.find_passages()
        if passages:
            self.queue.extend(passages)
        self.visited.add(self.curr)
        if self.curr == self.end:
            self.not_finished = False

    def find_passages(self):
        passages = []
        y, x = self.curr
        cell_directions = self.maze[y][x].__dict__

        for direction in ((0, 1), (1, 0), (0, -1), (-1, 0)):

            dir_name = self.direction_names[direction]
            if cell_directions[dir_name]:
                continue
            move = add_tuple(self.curr, direction)
            if move not in self.visited:
                passages.append(move)
        if self.use_manhattan_distance:
            passages.sort(key=self.manhattan_distance, reverse=True)
        return passages

    def manhattan_distance(self, pos):
        y1, x1 = pos
        y2, x2 = self.end
        dist = abs(x1 - x2) + abs(y1 - y2)
        return dist


if __name__ == '__main__':
    from tools import create_empty_maze
    from maze_generators import RandomizedDFS, maze_filler

    maze = create_empty_maze(100, 100)
    generator = RandomizedDFS((100, 100))
    maze_filler(maze, generator)
    solver = DFS(maze)

    while solver.not_finished:
        solver.move()

    print('Done')
