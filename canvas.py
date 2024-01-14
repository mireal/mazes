import PySimpleGUI as sg


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
    def __init__(self, cols, rows, cell_size, cell_color='lightgray', highlighted_cell_color='#58846d',
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

    def clear_canvas(self):
        canvas = sg.Graph(
            canvas_size=self.size,
            graph_bottom_left=self.graph_bottom_left,
            graph_top_right=self.graph_top_right,
            background_color=self.background_color
        )

        self.canvas = canvas

    def draw_finished_maze(self, maze):
        self.clear_canvas()
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


if __name__ == '__main__':
    from tools import create_empty_maze
    from maze_generators import RandomizedPrim, RandomizedDFS, maze_filler

    cell_size = 50
    cols = 20
    rows = 10

    dynamic_canvas = DynamicCanvas(cols, rows, cell_size)

    layout = [
        [dynamic_canvas.canvas]
    ]

    window = sg.Window('Maze test', layout, finalize=True, return_keyboard_events=True)

    maze = create_empty_maze(cols, rows)
    # generator = RandomizedPrim((cols, rows))
    generator = RandomizedDFS((cols, rows))

    update_speed = 100
    paused = True
    while True:
        event, values = window.read(timeout=update_speed)

        if event == sg.WIN_CLOSED:
            break
        elif type(event) == str and 'space' in event:
            paused = not paused
        if generator.not_finished and not paused:
            maze_filler(maze, generator, step_by_step=True)

            curr_pos = generator.curr
            y, x = curr_pos
            curr_cell = maze[y][x]

            prev_pos = generator.prev
            y, x = prev_pos
            prev_cell = maze[y][x]

            dynamic_canvas.draw_cell(prev_pos, prev_cell)
            dynamic_canvas.draw_cell(curr_pos, curr_cell)
            dynamic_canvas.draw_highlighted_cell(curr_pos)

    window.close()
