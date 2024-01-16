import PySimpleGUI as sg
from maze_generators import maze_filler
from tools import create_empty_maze


class CanvasCell:
    def __init__(self, canvas: sg.Graph, pos, cell_size, border_size, cell_color, border_color):
        self.canvas = canvas
        self.cell, self.borders = self.initialize(pos, cell_size, border_size, cell_color, border_color)

    def initialize(self, pos, cell_size, border_size, cell_color, border_color):
        border_size += 1
        y, x = pos
        rect_left = x * cell_size
        rect_top = y * cell_size

        top_left = (rect_left, rect_top)
        top_right = (rect_left + cell_size, rect_top)
        bottom_left = (rect_left, rect_top + cell_size)
        bottom_right = (rect_left + cell_size, rect_top + cell_size)

        cell = self.canvas.draw_rectangle(top_left, bottom_right, fill_color=cell_color, line_color=cell_color,
                                          line_width=1)

        top = self.canvas.draw_line(top_left, top_right, color=border_color, width=border_size)
        right = self.canvas.draw_line(top_right, bottom_right, color=border_color, width=border_size)
        bottom = self.canvas.draw_line(bottom_left, bottom_right, color=border_color, width=border_size)
        left = self.canvas.draw_line(top_left, bottom_left, color=border_color, width=border_size)

        borders = {'top': top, 'right': right, 'bottom': bottom, 'left': left}

        return cell, borders

    def update_borders(self, cell):
        self.canvas.send_figure_to_back(cell)
        cell_borders = cell.__dict__
        for border_name, visibility in cell_borders.items():
            line = self.borders[border_name]
            if visibility:
                self.canvas.bring_figure_to_front(line)
            else:
                self.canvas.delete_figure(line)


class DynamicCanvas:
    def __init__(self, cols, rows, cell_size, cell_color='lightgray',
                 highlighted_cell_color='#58846d',
                 background_color='grey', border_color='black'):
        self.cols = cols
        self.rows = rows

        self.cell_size = cell_size
        self.border_size = cell_size // 10

        self.size = (rows * cell_size + self.border_size * 2, cols * cell_size + self.border_size * 2)
        self.graph_top_right = (self.rows * self.cell_size + self.border_size, 0 - self.border_size)
        self.graph_bottom_left = (0 - self.border_size, self.cols * self.cell_size + self.border_size)

        self.cell_color = cell_color
        self.highlighted_cell_color = highlighted_cell_color
        self.background_color = background_color
        self.border_color = border_color

        self.canvas = sg.Graph(self.size, self.graph_bottom_left, self.graph_top_right, self.background_color)
        self.canvas_objects = dict()
        self.highlighted_cell = None

    def clear(self):
        self.canvas.erase()

    def draw_finished_maze(self, maze):
        self.clear()
        self.canvas_objects.clear()
        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                pos = (y, x)
                self.draw_cell(pos, cell)

    def draw_highlighted_cell(self, pos):
        if self.highlighted_cell:
            self.canvas.delete_figure(self.highlighted_cell)
        y, x = pos
        top_left = (x * self.cell_size + self.border_size, y * self.cell_size + self.border_size)
        bottom_right = (
            x * self.cell_size + self.cell_size - self.border_size,
            y * self.cell_size + self.cell_size - self.border_size)
        highlighted_cell = self.canvas.draw_rectangle(top_left, bottom_right,
                                                      fill_color=self.highlighted_cell_color,
                                                      line_color=self.highlighted_cell_color,
                                                      line_width=self.border_size)
        self.highlighted_cell = highlighted_cell

    def draw_cell(self, pos, cell):
        if pos not in self.canvas_objects:
            canvas_rectangle = CanvasCell(self.canvas, pos, self.cell_size, self.border_size, self.cell_color,
                                          self.border_color)
            self.canvas_objects[pos] = canvas_rectangle

        canvas_rectangle = self.canvas_objects[pos]
        canvas_rectangle.update_borders(cell)


class DynamicLayout:
    def __init__(self, generators: list, solvers: list, cols, rows, cell_size,
                 current_state='Generate'):
        self.window: sg.Window = None

        self.running = True
        self.paused = True
        self.speed = 10
        self.current_state = current_state

        self.cols, self.rows = cols, rows
        self.cell_size = cell_size

        self.generators = generators
        self.solvers = solvers

        self.algorithm_objects: list[RandomizedDFS] = []
        self.mazes = []
        self.update_algorithms(current_state)

        self.basic_maze_generator = generators[0]
        self.basic_maze = None

        self.maze_generator_choice = sg.Column([[
            sg.Text('Maze generator:'),
            # sg.Combo(self.generator_names, default_value=self.basic_maze_generator, visible=False, enable_events=True),
            sg.Push()]], visible=False)

        self.grid, self.canvas_objects = self.initialize_canvases()

        self.control_panel = sg.Column([
            [sg.Push(), sg.Button('Generate'), sg.Button('Solve'), sg.Push()],
            [self.maze_generator_choice],
            [sg.Push(), sg.Button('Start'), sg.Button('Pause'), sg.Push()],
            [sg.Button('Slower'), sg.Push(), sg.Button('Faster'), sg.Push()],
            [sg.Push(), sg.Button('Refresh'), sg.Push()],
        ])

        self.base_layout = [self.grid, self.control_panel]

    def initialize_canvases(self):
        canvases = []
        canvas_objects = []

        for i in range(4):
            canvas = DynamicCanvas(self.cols, self.rows, self.cell_size)
            canvas_objects.append(canvas)
            text = sg.Text('text')
            box = sg.Column([[text], [canvas.canvas]])
            canvases.append(box)

        grid = sg.Column([[canvases[0], canvases[1]],
                          [canvases[2], canvases[3]]])

        return grid, canvas_objects

    def update_canvases(self):
        if self.current_state == 'Solve':
            self.basic_maze = create_empty_maze(self.cols, self.rows)
            maze_filler(self.basic_maze, RandomizedDFS((self.cols, self.rows)))

        for canvas in self.canvas_objects:
            canvas.clear()
            if self.basic_maze:
                canvas.draw_finished_maze(self.basic_maze)

    def update_algorithms(self, state):
        algorithms = []
        algorithm_objects = []
        argument = ()
        if state == 'Generate':
            algorithms = self.generators
            argument = (self.cols, self.rows)
            self.mazes = [create_empty_maze(self.cols, self.rows) for i in range(4)]
        else:
            algorithms = self.solvers
            argument = self.basic_maze
        while len(algorithms) < 4:
            algorithms.extend(algorithms)

        for i in range(4):
            algorithm = algorithms[i](argument)
            algorithm_objects.append(algorithm)

        self.algorithm_objects = algorithm_objects[:4]

    def update_current_state(self, state):
        self.current_state = state
        self.paused = True
        self.update_canvases()

        visibility = True if state == 'Solve' else False
        self.maze_generator_choice.update(visible=visibility)
        self.update_algorithms(state)

    def move(self):
        for algorithm, canvas, maze in zip(self.algorithm_objects, self.canvas_objects, self.mazes):
            if algorithm.not_finished:
                if self.current_state == 'Generate':
                    maze_filler(maze, algorithm, step_by_step=True)
                else:
                    algorithm.move()

                curr_pos = algorithm.curr
                y, x = curr_pos
                curr_cell = maze[y][x]

                prev_pos = algorithm.prev
                y, x = prev_pos
                prev_cell = maze[y][x]

                canvas.draw_cell(prev_pos, prev_cell)
                canvas.draw_cell(curr_pos, curr_cell)
                canvas.draw_highlighted_cell(curr_pos)

    def event_handler(self):
        event, values = self.window.read(timeout=self.speed)
        if event == sg.WIN_CLOSED:
            self.running = False
            return
        if event in ('Generate', 'Solve') and event != self.current_state:
            print(event)
            print(self.canvas_objects)
            self.update_current_state(event)

        elif event in ('Start', 'Pause'):
            if event == 'Start' and self.paused:
                self.paused = not self.paused
            elif event == 'Pause' and not self.paused:
                self.paused = not self.paused

        elif event in ('Faster', 'Slower'):
            if event == 'Slower':
                self.speed += 100
            elif self.speed > 50:
                self.speed -= 50
            print(self.speed)

        elif event == 'Refresh':
            self.update_canvases()

        if not self.paused:
            self.move()

    def map_names_to_classes(self, classes: list):
        classes_map = {}
        for class_instance in classes:
            name = self.get_class_name(class_instance)
            classes_map[name] = class_instance

        return classes_map

    def get_class_name(self, class_instance):
        return class_instance.__class__.__name__


if __name__ == '__main__':
    from maze_generators import RandomizedDFS, RandomizedPrim, HuntAndKill, maze_filler
    from tools import create_empty_maze
    from maze_solvers import DFS

    generators = [RandomizedDFS, RandomizedPrim, HuntAndKill]
    solvers = [DFS]

    cols = rows = 40
    cell_size = 10

    sg.theme('Dark')

    LayoutController = DynamicLayout(generators, solvers, cols, rows, cell_size)

    separator = sg.VSeparator()

    layout = [LayoutController.grid, separator, LayoutController.control_panel]
    window = sg.Window('Window Title', [layout], finalize=True, return_keyboard_events=True)

    LayoutController.window = window

    while LayoutController.running:
        LayoutController.event_handler()
    window.close()
