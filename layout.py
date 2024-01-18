import PySimpleGUI as sg
from maze_generators import maze_filler
from tools import get_direction, reverse_tuple, directions, remove_border, create_empty_maze


class CanvasCell:
    def __init__(self, canvas: sg.Graph, pos, cell_size, border_size, cell_color, border_color):
        self.canvas = canvas
        self.pos, self.rectangle, self.borders = self.initialize(pos, cell_size, border_size, cell_color, border_color)

    def initialize(self, pos, cell_size, border_size, cell_color, border_color):
        border_size += 1
        y, x = pos
        rect_left = x * cell_size
        rect_top = y * cell_size

        top_left = (rect_left, rect_top)
        top_right = (rect_left + cell_size, rect_top)
        bottom_left = (rect_left, rect_top + cell_size)
        bottom_right = (rect_left + cell_size, rect_top + cell_size)

        pos = (top_left, bottom_right)

        cell = self.canvas.draw_rectangle(top_left, bottom_right, fill_color=cell_color, line_color=cell_color,
                                          line_width=1)

        top = self.canvas.draw_line(top_left, top_right, color=border_color, width=border_size)
        right = self.canvas.draw_line(top_right, bottom_right, color=border_color, width=border_size)
        bottom = self.canvas.draw_line(bottom_left, bottom_right, color=border_color, width=border_size)
        left = self.canvas.draw_line(top_left, bottom_left, color=border_color, width=border_size)

        borders = {'top': top, 'right': right, 'bottom': bottom, 'left': left}

        return pos, cell, borders

    def update_borders(self, cell):
        self.canvas.send_figure_to_back(self.rectangle)
        cell_borders = cell.__dict__
        for border_name, visibility in cell_borders.items():
            line = self.borders[border_name]
            if visibility:
                self.canvas.bring_figure_to_front(line)
            else:
                self.canvas.delete_figure(line)

    def change_color(self, new_color):
        self.canvas.delete_figure(self.rectangle)
        top_left, bottom_right = self.pos
        cell = self.canvas.draw_rectangle(top_left, bottom_right, fill_color=new_color, line_color=new_color,
                                          line_width=1)
        self.canvas.send_figure_to_back(cell)
        self.rectangle = cell


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

        self.textbox = sg.Text('Text')
        self.column = sg.Column([[self.textbox], [self.canvas]])

    def clear(self):
        """Call erase method for graph object, clear object dictionary"""
        self.canvas.erase()
        self.canvas_objects.clear()
        self.highlighted_cell = None

    def change_title(self, new_title):
        self.textbox.update(value=new_title)

    def draw_finished_maze(self, maze):
        self.clear()
        # self.change_cell_color((0, 0), self.highlighted_cell_color)
        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                pos = (y, x)
                self.draw_cell(pos, cell, self.cell_color)

    def draw_highlighted_cell(self, pos, erase_previous=True):
        if self.highlighted_cell and erase_previous:
            self.canvas.delete_figure(self.highlighted_cell)
        y, x = pos
        top_left = (x * self.cell_size + self.border_size, y * self.cell_size + self.border_size)
        bottom_right = (
            x * self.cell_size + self.cell_size - self.border_size,
            y * self.cell_size + self.cell_size - self.border_size)
        self.highlighted_cell = self.canvas.draw_rectangle(top_left, bottom_right,
                                                           fill_color=self.highlighted_cell_color,
                                                           line_color=self.highlighted_cell_color,
                                                           line_width=self.border_size)

    def draw_cell(self, pos: tuple, cell, color):
        if pos not in self.canvas_objects:
            canvas_rectangle = CanvasCell(self.canvas, pos, self.cell_size, self.border_size, color,
                                          self.border_color)
            self.canvas_objects[pos] = canvas_rectangle

        canvas_rectangle = self.canvas_objects[pos]
        canvas_rectangle.update_borders(cell)

    def change_cell_color(self, pos, new_color):
        cell = self.canvas_objects[pos]
        cell.change_color(new_color)


class DynamicLayout:
    def __init__(self, generators: list, solvers: list, cols, rows, cell_size,
                 current_state='Generate'):
        self.window = None

        self.running = True
        self.paused = True
        self.speed = 1000
        self.current_state = current_state

        self.cols, self.rows = cols, rows
        self.cell_size = cell_size

        self.generators = generators
        self.solvers = solvers

        self.algorithm_objects = []
        self.mazes = []
        self.grid, self.canvas_objects = self.initialize_canvases()

        self.generator_names_map = {generator.__name__: generator for generator in generators}
        generator_names = [generator.__name__ for generator in generators]

        self.basic_maze_generator = self.generator_names_map[generator_names[0]]
        self.basic_maze = None
        button_size = (15, 2)

        self.choice_box = sg.Combo(generator_names, default_value=generator_names[0], enable_events=True,
                                   key='-GENERATOR_CHOICE-', disabled=True)

        start_pause_button = sg.Button('Start / Pause', key='-STARTPAUSE-', size=button_size)
        refresh_button = sg.Button('↻', key='-REFRESH-', size=(2, 2))

        speed_plus_button = sg.Button('+', key='-FASTER-', size=(2, 2))
        speed_minus_button = sg.Button('-', key='-SLOWER-', size=(2, 2))
        speed_text = sg.Button('Speed', size=(10, 2), mouseover_colors=('black', 'white'))

        self.control_panel = sg.Column([
            [sg.Text('')],
            [sg.Button('Generate', size=button_size), sg.Push(), sg.Button('Solve', size=button_size)],
            [sg.Text('')],
            [sg.Push(), start_pause_button, refresh_button, sg.Push()],
            [sg.Text('')],
            [sg.Push(), speed_plus_button, speed_text, speed_minus_button, sg.Push()],
            [sg.Text('')],
            [sg.HSeparator()],
            [sg.Text('')],
            [sg.Text('Maze for solving: '), self.choice_box]
        ], expand_y=True)

        self.layout = [self.grid, sg.VSeparator(), self.control_panel]

    def initialize(self, window):
        self.window = window
        self.refresh()

    def initialize_canvases(self):
        canvases = []
        canvas_objects = []

        for i in range(4):
            canvas = DynamicCanvas(self.cols, self.rows, self.cell_size)
            canvas_objects.append(canvas)
            canvases.append(canvas.column)

        grid = sg.Column([[canvases[0], canvases[1]],
                          [canvases[2], canvases[3]]])

        return grid, canvas_objects

    def refresh(self):
        if self.current_state == 'Generate':
            self.basic_maze = None
            class_instances = self.generators
            argument = (self.cols, self.rows)
            self.mazes = [create_empty_maze(self.cols, self.rows) for _ in range(4)]
        else:
            class_instances = self.solvers
            self.basic_maze = create_empty_maze(self.cols, self.rows)
            maze_filler(self.basic_maze, self.basic_maze_generator((self.cols, self.rows)))
            argument = self.basic_maze

        class_objects = [inst(argument) for inst in class_instances]

        for class_object, canvas in zip(class_objects, self.canvas_objects):
            class_name = class_object.__class__.__name__
            canvas.clear()
            canvas.change_title(class_name)
            if self.basic_maze:
                canvas.draw_finished_maze(self.basic_maze)
                canvas.change_cell_color((0, 0), '#58846d')

        self.algorithm_objects = class_objects

    def generator_move(self, algorithm, canvas, maze):
        # maze_filler(maze, algorithm, step_by_step=True)
        curr_pos = algorithm.move()
        prev_pos = algorithm.prev

        y, x = curr_pos
        prev_y, prev_x = prev_pos

        curr_cell = maze[y][x]
        prev_cell = maze[prev_y][prev_x]

        direction = get_direction(curr_pos, prev_pos)
        reversed_direction = reverse_tuple(direction)

        direction_name = directions[direction]
        reversed_direction_name = directions[reversed_direction]

        remove_border(curr_cell, direction_name)
        remove_border(prev_cell, reversed_direction_name)

        canvas.draw_cell(prev_pos, prev_cell, 'lightgray')
        canvas.draw_cell(curr_pos, curr_cell, 'lightgray')

        canvas.draw_highlighted_cell(curr_pos)

    def solver_move(self, algorithm, canvas):
        algorithm.move()
        curr_pos = algorithm.curr
        canvas.change_cell_color(curr_pos, canvas.highlighted_cell_color)

    def move(self):
        if all(not alg.not_finished for alg in self.algorithm_objects):
            self.paused = True
            return
        for algorithm, canvas, maze in zip(self.algorithm_objects, self.canvas_objects, self.mazes):
            if algorithm.not_finished:
                if self.current_state == 'Generate':
                    self.generator_move(algorithm, canvas, maze)
                else:
                    self.solver_move(algorithm, canvas)

    def event_handler(self):
        event, values = self.window.read(timeout=self.speed)
        if event == sg.WIN_CLOSED:
            self.running = False
            return
        elif event in ('Generate', 'Solve') and event != self.current_state:
            # self.update_current_state(event)
            self.current_state = event
            self.refresh()
            disable = False if event == 'Solve' else True
            self.choice_box.update(disabled=disable)
        elif event == '-REFRESH-':
            self.paused = True
            self.refresh()
        elif event == '-STARTPAUSE-':
            self.paused = not self.paused
        elif event == '-FASTER-':
            self.speed //= 2
            print(self.speed)
        elif event == '-SLOWER-':
            if self.speed < 2:
                self.speed += 1
            else:
                self.speed *= 2
            print(self.speed)
        elif event == '-GENERATOR_CHOICE-':
            name = values[event]
            self.basic_maze_generator = self.generator_names_map[name]
            self.refresh()
        if not self.paused:
            self.move()


if __name__ == '__main__':
    from maze_generators import RandomizedDFS, RandomizedPrim, HuntAndKill, PlaceholderGenerator
    from maze_solvers import DFS, BFS, PriorityDFS, PlaceholderSolver

    generator_classes = [RandomizedDFS, RandomizedPrim, HuntAndKill, PlaceholderGenerator]
    solver_classes = [DFS, BFS, PriorityDFS, PlaceholderSolver]

    col_len = row_len = 40
    size = 10

    sg.theme('DarkTeal6')

    LayoutController = DynamicLayout(generator_classes, solver_classes, col_len, row_len, size)

    window = sg.Window('Window Title', [LayoutController.layout], finalize=True, return_keyboard_events=True)

    LayoutController.initialize(window)

    while LayoutController.running:
        LayoutController.event_handler()
    window.close()
