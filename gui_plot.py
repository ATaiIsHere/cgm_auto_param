import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import *
from tkinter import ttk, messagebox


class PlotGUI(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        # self.pack()

        self.f = Figure(figsize=(13, 5), dpi=100)
        self.f.subplots_adjust(left=0.05, right=0.99, top=0.9, bottom=0.1)
        self.f_plot = self.f.add_subplot(111)
        self.canvs = FigureCanvasTkAgg(self.f, self)
        self.canvs.get_tk_widget().grid(row=0, column=1, rowspan=9, columnspan=9)

        self.entry_ymax = ttk.Entry(self)
        self.entry_ymax['width'] = 5
        self.entry_ymax.grid(row=0, column=0)

        self.entry_ymin = ttk.Entry(self)
        self.entry_ymin['width'] = 5
        self.entry_ymin.grid(row=8, column=0)

        self.entry_xmax = ttk.Entry(self)
        self.entry_xmax['width'] = 5
        self.entry_xmax.grid(row=9, column=8)

        self.entry_xmin = ttk.Entry(self)
        self.entry_xmin['width'] = 5
        self.entry_xmin.grid(row=9, column=1)

        # self.button = ttk.Button(self)
        # self.button["text"] = "data1!"
        # self.button["command"] = self.insert_data1
        # self.button.grid(row=2, column=0)
        #
        # self.button = ttk.Button(self)
        # self.button["text"] = "data2!"
        # self.button["command"] = self.insert_data2
        # self.button.grid(row=3, column=0)

        self.lim_button_set = ttk.Button(self)
        self.lim_button_set["text"] = "Set x/y limit"
        self.lim_button_set["command"] = self.reset_limit
        self.lim_button_set.grid(row=4, column=0)

        self.button = ttk.Button(self)
        self.button["text"] = "pop!"
        self.button["command"] = self.pop_data
        self.button.grid(row=5, column=0)

        self.reset_limit()

    def reset_limit(self):
        y_bottom = None if not self.entry_ymin.get() else float(self.entry_ymin.get())
        y_top = None if not self.entry_ymax.get() else float(self.entry_ymax.get())
        x_left = None if not self.entry_xmin.get() else float(self.entry_xmin.get())
        x_right = None if not self.entry_xmax.get() else float(self.entry_xmax.get())
        print(self.entry_ymax.get())
        print(y_bottom, y_top, x_left, x_right)

        # self.f_plot.clear()
        self.f_plot.autoscale()
        if y_bottom and y_top:
            self.f_plot.set_ylim(y_bottom, y_top)
        if x_left and x_right:
            self.f_plot.set_xlim(x_left, x_right)

        self.canvs.draw()

    def plot_boundary(self, x=None, y=None, color='r', linewidth=1):
        if x:
            self.f_plot.axvline(x, color=color, linewidth=linewidth)
        if y:
            self.f_plot.axhline(y, color=color, linewidth=linewidth)

    def push_data(self, x, y, marker='-'):
        self.f_plot.plot(x, y, marker)
        self.canvs.draw()

    def pop_data(self):
        self.f_plot.lines[len(self.f_plot.lines)-1].remove()
        self.canvs.draw()

    def clear_data(self):
        self.f_plot.clear()
        self.canvs.draw()

    def insert_data1(self):
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        y = [3, 6, 9, 12, 15, 18, 15, 12, 15, 18]
        # self.f_plot.clear()
        self.push_data(x, y)

    def insert_data2(self):
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        y = [3, 6, 9, 12, 10, 10, 15, 12, 15, 18]
        # self.f_plot.clear()
        self.push_data(x, y)

    def save_fig(self, fname):
        self.f.savefig(fname)


if __name__ == '__main__':
    root = Tk()
    root.title("Plot GUI")

    app = PlotGUI(root)
    app.grid(row=0, column=0)

    root.mainloop()
