from tkinter import *
from gui_plot import PlotGUI
from gui_data_process import DataProcessGUI
import os


def draw_CGM(data_process_gui, plot_gui):
    x, y = data_process_gui.get_cgm_data(kalman=False)
    plot_gui.push_data(x, y)


def draw_BGM(data_process_gui, plot_gui):
    x, y = data_process_gui.get_bgm_data()
    plot_gui.push_data(x, y, marker='-o')


def draw_means(data_process_gui, plot_gui, n, shift):
    x, y = data_process_gui.get_n_points_window_vals(n, shift, window_type='mean')
    plot_gui.push_data(x, y, marker='o')


def draw_medians(data_process_gui, plot_gui, n, shift):
    x, y = data_process_gui.get_n_points_window_vals(n, shift, window_type='median')
    plot_gui.push_data(x, y, marker='o')


def macro_1(data_process_gui, plot_gui, k, shift):
    plot_gui.clear_data()
    data_process_gui.load_data_info()
    plot_gui.plot_boundary(x=data_process_gui.get_steady_start(), linewidth=2)
    plot_gui.plot_boundary(x=data_process_gui.find_steady_start(), linewidth=2, color='b')
    draw_BGM(data_process_gui, plot_gui)
    draw_CGM(data_process_gui, plot_gui)
    draw_medians(data_process_gui, plot_gui, k, shift)



if __name__ == '__main__':
    root = Tk()
    root.title("Main")
    plot_gui = PlotGUI(root)
    data_process_gui = DataProcessGUI(root)
    feature_panel = Frame()

    plot_gui.grid(row=0, column=0)
    data_process_gui.grid(row=1, column=0, sticky=W)
    feature_panel.grid(row=2, column=0, sticky=W)

    Button(feature_panel, text='Draw CGM', command=lambda: draw_CGM(data_process_gui, plot_gui))\
        .grid(row=0, column=0, sticky=W)
    Button(feature_panel, text='Draw BGM', command=lambda: draw_BGM(data_process_gui, plot_gui))\
        .grid(row=0, column=1, sticky=W)

    k = Entry(feature_panel, width=5)
    k.insert(0, "720")
    k.grid(row=1, column=0)

    shift = Entry(feature_panel, width=5)
    shift.insert(0, "60")
    shift.grid(row=1, column=1)

    Button(feature_panel,
           text='Draw means',
           command=lambda: draw_means(data_process_gui, plot_gui, int(k.get()), int(shift.get()))) \
        .grid(row=1, column=2, sticky=W)

    Button(feature_panel,
           text='Draw medians',
           command=lambda: draw_medians(data_process_gui, plot_gui, int(k.get()), int(shift.get()))) \
        .grid(row=1, column=3, sticky=W)

    Button(feature_panel,
           text='Save figure',
           command=lambda: plot_gui.save_fig(os.getcwd() + '/' + data_process_gui.entry_data_dir.get().split('/')[-1] + '.png')) \
        .grid(row=1, column=4, sticky=W)

    Button(feature_panel,
           text='Macro 1',
           command=lambda: macro_1(data_process_gui, plot_gui, int(k.get()), int(shift.get()))) \
        .grid(row=1, column=5, sticky=W)

    root.mainloop()
