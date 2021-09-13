import tkinter as tk


class MenuBar(tk.Menu):
    def __init__(self, master, controller, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self.master = master
        self.controller = controller
        self._init_menu()

    def _init_menu(self):
        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_command(label='Beginner', command=lambda: self.on_difficulty_change('beginner'))
        file_menu.add_command(label='Intermediate', command=lambda: self.on_difficulty_change('intermediate'))
        file_menu.add_command(label='Expert', command=lambda: self.on_difficulty_change('expert'))
        file_menu.add_command(label='Custom', command=lambda: self.on_difficulty_change('custom'))
        file_menu.add_separator()
        file_menu.add_command(label="Reveal All", command=self.reveal_all)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.quit)
        self.add_cascade(label='File', menu=file_menu)

        help_menu = tk.Menu(self, tearoff=False)
        help_menu.add_command(label='About...', command=self.about)
        self.add_cascade(label='Help', menu=help_menu)

        self.master.config(menu=self)

    def on_difficulty_change(self, difficulty):
        try:
            isinstance(difficulty, str)
            self.controller.on_difficulty_change(difficulty)
        except TypeError as e:
            print(e)
            return

    def reveal_all(self):
        self.controller.reveal_all()

    def quit(self):
        self.controller.quit()

    def about(self):
        self.controller.about()
