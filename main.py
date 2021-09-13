#  import pprint as pp  # DEBUG
import random
import os
import tkinter as tk
from tkinter import ttk
from enum import Enum
from collections import namedtuple
from PIL import ImageTk, Image
from menu import MenuBar

#################
# -- GLOBALS -- #
#################

# random.seed(2)  # DEBUG

root = tk.Tk()

Difficulty = namedtuple("Beginner", "mines cols rows")

difficulty_dict = {
    'beginner': Difficulty(10, 9, 9),
    'intermediate': Difficulty(40, 15, 15),
    'expert': Difficulty(99, 30, 16)
}


########################
# --STATIC FUNCTIONS-- #
########################


def load_images() -> dict:
    """
    Uses the PIL module to load and convert png files for use by tkinter
    :return: dict: dict:key: image name, dict:value: ImageTK.Photoimage object
    """
    image_dict = {}
    image_files = os.listdir(f"{os.getcwd()}/images")
    for file in image_files:
        image_dict[file[:-4]] = ImageTk.PhotoImage(Image.open(f"images/{file}"))
    return image_dict


def generate_minefield(mines, cols, rows) -> list:
    """
    Generates a 2D list of string value representing the state of a tile.
    A number (0-8) denotes the total number of mines found on it's 8 adjacent neighbors
    An 'x' denotes a mine
    :param mines: number of mines
    :param cols: number of cols
    :param rows: number of rows
    :return: list
    """
    probability = mines / (cols * rows)

    grid = [["." for _ in range(cols)] for _ in range(rows)]

    mine_count = mines

    # Add Mines
    y_index = 0
    x_index = 0

    while mine_count > 0:
        # DEBUG
        # random.seed(1234)

        if random.random() < probability:
            try:
                grid[y_index][x_index] = "X"
                mine_count -= 1
            except IndexError as e:
                print(e)
                print(f"y: {y_index}, x: {x_index}")
                print(f"grid max: {len(grid)},{len(grid[0])}")

        x_index = (x_index + 1) % cols
        if x_index == 0:
            y_index = (y_index + 1) % rows

    # add numbers

    for grid_y, row in enumerate(grid):
        for grid_x, cell in enumerate(row):

            # Check all 8 adjacent neighbors
            count = 0
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if grid[grid_y][grid_x] == "X":
                        continue
                    if (
                            grid_y + i < 0
                            or grid_y + i > rows - 1
                            or grid_x + j < 0
                            or grid_x + j > cols - 1
                    ):
                        continue
                    if i == 0 and j == 0:
                        continue

                    if grid[grid_y + i][grid_x + j] == "X":
                        count += 1
                    if count > 0:
                        grid[grid_y][grid_x] = str(count)
                    else:
                        grid[grid_y][grid_x] = str(0)

    # DEBUG
    # pp.pprint(grid)
    return grid


def edge_case(dx, dy, width, height) -> bool:
    return dx < 0 or dx > width - 1 or dy < 0 or dy > height - 1


###############
# --CLASSES-- #
###############


class GameState(Enum):
    """
    Enum holding game state
    """
    IDLE = 0
    PLAYING = 1


class Tile:
    """
    Tile Class used to visually represent a clickable tile
    """

    def __init__(self, master, controller, x, y, image, value):
        """
        Init method of Tile class
        :param master: tk.Widget object acting as master for tk.Label widget of Tile class
        :param controller: game controller object
        :param x: index of column
        :param y: index of row
        :param image: ImageTk.Photoimage object
        :param value: string value of tile representing a mine or a number from 0-9 representeing
        the number of mines around it's 8 adjacent neighbors
        """
        self.label = tk.Label(master, image=image)
        # super().__init__(master, image=image)
        self.master = master
        self.controller = controller
        self.x = x
        self.y = y
        self.image = image
        self.value = value

        self.revealed = False
        self._mouse_right_pressed = False

        self.entered = False
        self.flagged = False
        self._set_binds()

    def _set_binds(self) -> None:
        """
        Binds mouse events (enter, leave, click, press, release) to tk.Label attribute of Tile Class
        :return: None
        """
        if self.controller.game_state == GameState.PLAYING:
            self.label.bind("<Enter>", self._on_enter)
            self.label.bind("<Leave>", self._on_leave)
            self.label.bind("<Button-1>", self._on_click)
            self.label.bind("<Button-3>", self._on_right_click)
            self.label.bind("<ButtonPress-3>", self._on_right_mouse_down)
            self.label.bind("<ButtonRelease-3>", self._on_right_mouse_up)

    def _on_enter(self, event) -> None:
        """
        Handles mouse-entered event on tk.Label object of Tile class
        :param event:
        :return: None
        """
        # print(f"Entering: {self.x}, {self.y}")
        self.entered = True
        self._update_image()

    def _on_leave(self, event) -> None:
        """
        Handles mouse-exit event on tk.Label object of Tile class
        :param event:
        :return: None
        """
        # print(f"Leaving:  {self.x}, {self.y}")
        self.entered = False
        self._update_image()

    def _on_click(self, event) -> None:
        """
        Handles mouse-click (once) event on tk.Label object of Tile class
        :param event:
        :return: None
        """
        # print(f"Mouse L: {self.x}, {self.y}")
        if self.controller.game_state == GameState.PLAYING:
            if not self.revealed:
                if self.value == '0':
                    self.controller.recursive_reveal(self)
                else:
                    self.reveal_tile()
            else:
                if self._mouse_right_pressed and int(self.value) in range(1, 9):
                    self.controller.reveal_flagged(self)

    def _on_right_click(self, event) -> None:
        """
        Handles mouse-rightclick (once) event on tk.Label object of Tile class
        :param event:
        :return: None
        """
        # print(f"Mouse R: {self.x}, {self.y}")
        pass

    def _on_right_mouse_down(self, event) -> None:
        """
        Handles mouse-right pressed (held) event on tk.Label object of Tile class
        :param event:
        :return: None
        """
        # print(f"Mouse Down: {self.x}, {self.y}")
        if self.controller.game_state == GameState.PLAYING:
            if not self.revealed:
                self.flagged = not self.flagged
                self._update_image()
                self.controller.update_flagged(self)
            else:
                self._mouse_right_pressed = True

    def _on_right_mouse_up(self, event) -> None:
        """
        Handles mouse-right released event on tk.Label object of Tile class
        :param event:
        :return: None
        """
        # print(f"Mouse Up:   {self.x}, {self.y}")
        self._mouse_right_pressed = False

    def _update_image(self) -> None:
        """
        Updates the image attribute of the tk.Label object of the Tile class based on the state of the Tile
        :return: None
        """
        # image = self.image
        if not self.revealed:
            if self.entered:
                if self.flagged:
                    image = self.controller.images['flag_hover']
                else:
                    image = self.controller.images['tile_hover']
            else:
                if self.flagged:
                    image = self.controller.images['flag_normal']
                else:
                    image = self.controller.images['tile_normal']
        else:
            image = self.controller.images[self.value]
        self.label.config(image=image)
        self.image = image

    def reveal_tile(self) -> None:
        """
        Changes the image of the tile to reveal the value
        :return: None
        """
        if not self.flagged:
            self.revealed = True
            self._update_image()
            self.controller.revealed_count += 1
            if self.value == 'X':
                self.controller.game_over()
                # print("GAME OVER")  # DEBUG
            else:
                self.controller.check_win()

    def place(self) -> None:
        """
        Uses the tk.Place packer to render tk.Label image
        :return: None
        """
        x_pos = self.controller.cell_size * self.x + (1 * self.x)
        y_pos = self.controller.cell_size * self.y + (1 * self.y)
        self.label.place(x=x_pos, y=y_pos)

    def __str__(self):
        return f"<TILE {self.x}, {self.y}>"


class Board:
    """
    Board class representing all the Tile objects in PySweeper
    """

    def __init__(self, master, controller):
        """
        Init method of Board class
        :param master: tk.Widget object acting as master for tk.frame widget of Board class
        :param controller: game controller object
        """
        self.master = master
        self.controller = controller
        self.frame = tk.Frame(self.master)
        self._config_frame()

    def _config_frame(self) -> None:
        """
        Sets width and height of tk.Frame widget of Board class
        :return: None
        """
        width = self.controller.cols * self.controller.cell_size
        height = self.controller.rows * self.controller.cell_size

        self.frame.config(width=width, height=height)

    def place_tiles(self) -> None:
        """
        Renders all Tile objects to tk.Frame object of Board class
        :return: None
        """
        for y in range(self.controller.rows):
            for x in range(self.controller.cols):
                tile = self.controller.tilegrid[y][x]
                tile.place()

    def show(self) -> None:
        """
        Renders tk.Frame object of Board class
        :return:
        """
        self.frame.pack(expand=True, fill=tk.BOTH, pady=2)


class Timer(tk.Label):
    """
    Timer class used to increment the timer
    """
    def __init__(self, master, controller, text=000, font=("Arial", 20)):
        """
        Init method of Board class
        :param master: parent widget
        :param controller: game controller
        :param text: text for timer [optional]
        :param font: font family for timer [optional]
        """
        super().__init__(master, text=text, font=font)
        self.controller = controller
        self.master = master

        self.config(borderwidth=3, relief=tk.RIDGE)

        self.counter = -1
        self.running = False
        self.job_id = 0

    def reset(self) -> None:
        """
        Stops counter and resets timer
        :return: None
        """
        self.stop()
        self.counter = -1
        self.config(text="000")

    def start(self) -> None:
        """
        Starts timer
        :return: None
        """
        self.running = True
        self.controller.root.after(0, self.update)

    def update(self) -> None:
        """
        Updates timer after 1000 ms
        :return: None
        """
        if self.running:
            self.counter += 1
            c_string = f"{self.counter:03}"
            self.config(text=c_string)
            self.job_id = self.controller.root.after(1000, self.update)

    def stop(self) -> None:
        """
        Stops timer
        :return: None
        """
        if self.running:
            self.running = False
            self.controller.root.after_cancel(self.job_id)


class HotBar:
    """
    Hotbar class that holds number of mines, start button and timer
    """
    def __init__(self, master, controller) -> None:
        """
        Init method of Hotbar class
        :param master: parent widget
        :param controller: game controller
        """
        self.master = master
        self.controller = controller
        self.frame = tk.Frame(master, height=40, width=master.winfo_width(), borderwidth=1, relief=tk.RIDGE)

        self.mine_var = tk.StringVar(self.frame, "00")
        self.mine_label = tk.Label(self.frame, textvariable=self.mine_var, font=('Arial', 20))
        self.mine_label.config(borderwidth=3, relief=tk.RIDGE)
        self.mine_label.pack(padx=(5, 0), pady=(5, 5), side=tk.LEFT)

        self.mine_label_image = tk.Label(self.frame, image=self.controller.images['X'])
        self.mine_label_image.pack(padx=10, side=tk.LEFT)

        self.start_button = tk.Button(self.frame, image=self.controller.images['idle'])
        self.start_button.config(font=("Arial", 15))
        self.start_button.pack(padx=(10, 10), pady=(5, 5), side=tk.LEFT, expand=True)

        self.start_button.bind("<Button-1>", self._start_game)

        self.timer_image = tk.Label(self.frame, image=self.controller.images['timer'])
        self.timer_image.pack(padx=10, side=tk.LEFT)

        self.timer = Timer(self.frame, self.controller, text="000", font=("Arial", 20))
        self.timer.pack(padx=(0, 5), pady=(5, 5), side=tk.LEFT)

    def _start_game(self, event) -> None:
        """
        Starts Game
        :param event:
        :return: None
        """
        self.controller.start_game()
        self.update_button_image()

    def update_mine_label(self, value) -> None:
        """
        Updates the number of mines left
        :param value: value of mines left
        :return: None
        """
        var = f"{value:02}"
        self.mine_var.set(var)
        self.controller.root.update_idletasks()

    def update_button_image(self) -> None:
        """
        Update the image on the start button based on game_state
        :return:
        """
        if self.controller.game_state == GameState.IDLE:
            self.start_button.config(image=self.controller.images['idle'])
        elif self.controller.game_state == GameState.PLAYING:
            self.start_button.config(image=self.controller.images['playing'])


class PySweeper:
    """
    Game controller class that holds game logic
    """
    def __init__(self, rt: tk.Tk):
        """
        Init method of PySweeper class
        :param rt: root tk window (tk.Tk object)
        """
        self.cell_size = 30
        self.game_state = GameState.IDLE
        self.revealed_count = 0
        self.root = rt
        self.images = load_images()
        self._init_gui()
        self.minefield = None
        self.tilegrid = None

        self.on_difficulty_change('beginner')

    def _init_gui(self) -> None:
        """
        method that initializes gui options
        :return: None
        """
        self.root.title("PySweeper")
        self.root.resizable(False, False)
        self._add_menubar()
        self._add_hotbar()

    def _change_difficulty(self, diff) -> None:
        self.difficulty = diff
        level = difficulty_dict[diff]
        self.mines = level.mines
        self.tiles_flagged = 0
        self.revealed_count = 0
        self.cols = level.cols
        self.rows = level.rows
        self.hotbar.update_mine_label(self.mines - self.tiles_flagged)

    def _add_hotbar(self) -> None:
        self.hotbar = HotBar(self.root, self)
        self.hotbar.frame.pack(fill=tk.X)

        # self.root.update()
        # print(self.hotbar.frame.winfo_width(), self.hotbar.frame.winfo_height())

    def _add_board(self) -> None:
        self.board = Board(self.root, self)
        self.tilegrid = self._generate_tilegrid()
        self.board.place_tiles()
        self.board.show()
        width = self.cell_size * self.cols + self.cols + 2
        height = self.cell_size * self.rows + self.rows + 2
        self._set_geometry(width, height + 55)

    def _set_geometry(self, width, height):
        self.root.geometry(f"{width}x{height}")

    def _add_menubar(self) -> None:
        menu_bar = MenuBar(master=self.root, controller=self)
        self.root.config(menu=menu_bar)

    def _generate_tilegrid(self) -> list:
        grid = []
        for y in range(self.rows):
            row = []
            for x in range(self.cols):
                image = self.images['tile_normal']
                value = self.minefield[y][x]
                tile = Tile(self.board.frame, self, x, y, image, value)
                row.append(tile)
            grid.append(row)

        return grid

    def _get_adjacent_tiles(self, tile) -> list:
        tiles = []
        for i in range(-1, 2):
            for j in range(-1, 2):

                if edge_case(tile.x + j, tile.y + i, self.cols, self.rows):
                    continue

                if i == 0 and j == 0:
                    continue

                tiles.append(self.tilegrid[tile.y + i][tile.x + j])
        return tiles

    def _get_flagged_count(self, tiles) -> int:
        flagged = 0
        for tile in tiles:
            if tile.flagged:
                flagged += 1

        return flagged

    def start_game(self) -> None:
        if self.game_state == GameState.IDLE:
            self.game_state = GameState.PLAYING
            self.on_difficulty_change(self.difficulty)
            self.hotbar.timer.reset()
            self.hotbar.timer.start()

    def on_difficulty_change(self, difficulty) -> None:
        self._change_difficulty(difficulty)
        self.minefield = generate_minefield(self.mines, self.cols, self.rows)
        self.draw()

    def draw(self):
        if hasattr(self, 'board'):
            self.board.frame.destroy()
            self.__delattr__('board')

        self._add_board()

    def update_flagged(self, tile):
        if tile.flagged:
            self.tiles_flagged += 1
        else:
            self.tiles_flagged -= 1
        self.hotbar.update_mine_label(self.mines - self.tiles_flagged)

    def check_win(self):
        # print(self.revealed_count)  # DEBUG
        if self.revealed_count == self.rows * self.cols - self.mines:
            # print("WINNER")  # DEBUG
            self.win()

    def win(self):
        self.game_state = GameState.IDLE
        time_beaten = self.hotbar.timer.counter
        self.hotbar.timer.stop()

        self.win_window(time_beaten)

    def win_window(self, time):
        window = tk.Toplevel(self.root)
        window.grab_set()
        window.focus_set()
        window.title("Winner!")
        window.geometry("200x130")
        window.resizable(False, False)

        t = f"""
        WINNER!
        
        time: {time} seconds
        """
        ok_button = ttk.Button(window, text="Close", command=lambda: window.destroy())
        text_box = tk.Label(window)
        text_box.config(wraplength=180)
        text_box.config(text=t, font=("Arial", 12))

        text_box.pack()
        ok_button.pack()

    def reveal_flagged(self, tile):
        # print(f"Tile: {tile}")  # DEBUG
        # print(f"{tile.value}")  # DEBUG
        tiles = self._get_adjacent_tiles(tile)
        flagged_count = self._get_flagged_count(tiles)

        if flagged_count == int(tile.value):
            for t in tiles:
                if not t.revealed and not t.flagged:
                    if t.value == 'X':
                        t.reveal_tile()

                    elif t.value == '0':
                        self.recursive_reveal(t)

                    else:
                        t.reveal_tile()

    def recursive_reveal(self, tile) -> None:
        """
        Recursively reveal blank tiles
        :param tile: Reference to Tile object
        :return: None
        """

        tile.reveal_tile()
        adjacent_tiles = self._get_adjacent_tiles(tile)
        for node in adjacent_tiles:
            if node.revealed:
                continue

            if int(node.value) > 0:
                node.reveal_tile()

            if int(node.value) == 0:
                self.recursive_reveal(node)

    def reveal_all(self) -> None:
        for row in self.tilegrid:
            for tile in row:
                tile.reveal_tile()
        self.game_over()

    def game_over(self):
        self.game_state = GameState.IDLE
        self.hotbar.timer.stop()
        self.reveal_mines()
        self.hotbar.update_button_image()

    def reveal_mines(self):
        for row in self.tilegrid:
            for tile in row:
                if tile.value == 'X':
                    tile.revealed = True
                    tile._update_image()

    def quit(self) -> None:
        self.root.destroy()

    def about(self) -> None:
        window = tk.Toplevel(self.root)
        window.grab_set()
        window.focus_set()
        window.title("About")
        window.geometry("300x130")
        window.resizable(False, False)

        t = """Minesweeper clone made in vanilla python.

        For more info go to 
        {insert link here}
        """
        ok_button = ttk.Button(window, text="Close", command=lambda: window.destroy())
        text_box = tk.Label(window)
        text_box.config(wraplength=180)

        text_box.pack()
        ok_button.pack()

        text_box.config(text=t)


if __name__ == '__main__':
    game = PySweeper(root)
    game.root.mainloop()
