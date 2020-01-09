from tkinter import *
from gui_plot import PlotGUI
from gui_data_process import DataProcessGUI
import data_process
import numpy as np
import os


def draw_CGM(data_process_gui, plot_gui, kalman=False, lagging=0):
    x, y = data_process_gui.get_cgm_data(kalman=kalman, lagging=lagging)
    plot_gui.push_data(x, y)


def draw_BGM(data_process_gui, plot_gui):
    x, y = data_process_gui.get_bgm_data()
    plot_gui.push_data(x, y, marker='-o')


def set_limit_steady_range(data_process_gui, plot_gui):
    start, end = data_process_gui.get_steady_range()
    plot_gui.entry_xmin.delete(0, END)
    plot_gui.entry_xmin.insert(0, start)
    plot_gui.entry_xmax.delete(0, END)
    plot_gui.entry_xmax.insert(0, end)
    plot_gui.reset_limit()


def draw_means(data_process_gui, plot_gui, n, shift):
    x, y = data_process_gui.get_n_points_window_vals(n, shift, window_type='mean')
    plot_gui.push_data(x, y, marker='o')


def draw_medians(data_process_gui, plot_gui, n, shift):
    x, y = data_process_gui.get_n_points_window_vals(n, shift, window_type='median')
    plot_gui.push_data(x, y, marker='o')


# for find steady start
def cgm_fft(data_process_gui, plot_gui):
    plot_gui.clear_data()
    data_process_gui.load_data_info()
    y = data_process_gui.cgm_data
    x = np.linspace(1, len(y), len(y)) * 1440 / len(y)
    y = np.fft.fft(y)[::-1][:len(y)//2]
    y = np.abs(y)
    plot_gui.push_data(x[:len(x)//2], y)


# for find steady start
def macro_1(data_process_gui, plot_gui, k, shift):
    plot_gui.clear_data()
    data_process_gui.load_data_info()
    plot_gui.plot_boundary(x=data_process_gui.get_steady_range()[0], linewidth=2)
    plot_gui.plot_boundary(x=data_process_gui.find_steady_start(), linewidth=2, color='b')
    draw_BGM(data_process_gui, plot_gui)
    draw_CGM(data_process_gui, plot_gui)
    draw_medians(data_process_gui, plot_gui, k, shift)


# show all bgm/cgm mapping points in steady (current)
def macro_2(data_process_gui, plot_gui):
    plot_gui.clear_data()
    data_process_gui.load_data_info()
    start, end = data_process_gui.get_steady_range()
    x, y, idx = data_process_gui.get_bgm_cgm_mapping_list(range(start, end))
    x, y = np.array(x), np.array(y)
    sorted_idx = np.argsort(y)
    target_idx = np.append(sorted_idx[:10], sorted_idx[-10:])
    a, b = data_process.linear_regression(x[target_idx], y[target_idx])
    # a, b = data_process.linear_regression(x, y)
    plot_gui.plot_line_by_param(a, b, maximum=max(x), minimum=min(x))
    plot_gui.push_data(x, y, marker='o')
    plot_gui.push_data(x[target_idx], y[target_idx], marker='o')


# show all bgm/cgm mapping points in steady (base)
def macro_3(data_process_gui, plot_gui):
    plot_gui.clear_data()
    data_process_gui.load_data_info()
    start, end = data_process_gui.get_steady_range()
    x, y, idx = data_process_gui.get_bgm_cgm_mapping_list(range(start, end))
    a, b = data_process.linear_regression(x, y)
    plot_gui.plot_line_by_param(a, b, maximum=max(x), minimum=min(x))
    plot_gui.push_data(x, y, marker='o')
    plot_gui.push_data(x, y, marker='o')


# show all bgm/cgm mapping points in steady (split 1440 min)
def macro_4(data_process_gui, plot_gui):
    plot_gui.clear_data()
    data_process_gui.load_data_info()
    start, end = data_process_gui.get_steady_range()
    x, y, idx = data_process_gui.get_bgm_cgm_mapping_list(range(start, end))

    group_x, group_y = {}, {}
    for cgm, bgm, i in zip(x, y, idx):
        if group_x.get(i//1440) is None:
            group_x[i//1440] = []
            group_y[i // 1440] = []
        group_x[i // 1440].append(cgm)
        group_y[i // 1440].append(bgm)

    for key in group_x.keys():
        plot_gui.push_data(group_x[key], group_y[key], marker='o')


def macro_5(data_process_gui, plot_gui):
    plot_gui.clear_data()
    data_process_gui.load_data_info()
    start, end = data_process_gui.get_steady_range()
    points = data_process_gui.get_bgm_cgm_mapping_points(range(start, end))

    selected_points = []
    points_cluster = {}

    for p in points:
        y = p.get('y')
        label = y // 10
        if points_cluster.get(label) is None:
            points_cluster[label] = []
        points_cluster[label].append(p)

    for label in points_cluster:
        pts = points_cluster.get(label)
        if len(pts) < 3:
            continue
        pts = sorted(pts, key=lambda pt: pt.get('x'))
        median_point = pts[len(pts) // 2]
        selected_points.append(median_point)

    selected_x = list(map(lambda p: p.get('x'), selected_points))
    selected_y = list(map(lambda p: p.get('y'), selected_points))

    a, b = data_process.linear_regression(selected_x, selected_y)

    plot_gui.plot_line_by_param(a, b, maximum=max(selected_x), minimum=min(selected_x))
    plot_gui.push_points(points)
    plot_gui.push_points(selected_points)


# batch process
def batch_macro(data_process_gui, plot_gui, k, shift):
    root_dir = '/Users/sean.tai/PycharmProjects/cgm_auto_param/__T11Data'
    save_dir = '/Users/sean.tai/PycharmProjects/cgm_auto_param/__T11Result'

    filenames = filter(lambda filename: '_T' in filename, os.listdir(root_dir))
    for filename in filenames:
        filename = root_dir + '/' + filename
        print('batch: ', filename)
        data_process_gui.entry_data_dir.delete(0, END)
        data_process_gui.entry_data_dir.insert(0, filename)
        macro_5(data_process_gui, plot_gui)
        plot_gui.reset_limit()
        plot_gui.save_fig(os.getcwd() + '/' + data_process_gui.entry_data_dir.get().split('/')[-1] + '.png')


if __name__ == '__main__':
    root = Tk()
    root.title("Main")
    plot_gui = PlotGUI(root)
    data_process_gui = DataProcessGUI(root)
    feature_panel = Frame()

    plot_gui.grid(row=0, column=0)
    data_process_gui.grid(row=1, column=0, sticky=W)
    feature_panel.grid(row=2, column=0, sticky=W)

    Button(feature_panel, text='Draw origin CGM', command=lambda: draw_CGM(data_process_gui, plot_gui)) \
        .grid(row=0, column=0, sticky=W)
    Button(feature_panel, text='Draw CGM', command=lambda: draw_CGM(data_process_gui, plot_gui, True, 8))\
        .grid(row=0, column=1, sticky=W)
    Button(feature_panel, text='Draw BGM', command=lambda: draw_BGM(data_process_gui, plot_gui))\
        .grid(row=0, column=2, sticky=W)
    Button(feature_panel, text='Only steady', command=lambda: set_limit_steady_range(data_process_gui, plot_gui)) \
        .grid(row=0, column=3, sticky=W)

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
           text='Batch Macro',
           command=lambda: batch_macro(data_process_gui, plot_gui, int(k.get()), int(shift.get()))) \
        .grid(row=1, column=5, sticky=W)

    Button(feature_panel,
           text='Macro 1',
           command=lambda: macro_1(data_process_gui, plot_gui, int(k.get()), int(shift.get()))) \
        .grid(row=1, column=6, sticky=W)

    Button(feature_panel,
           text='Macro 2',
           command=lambda: macro_2(data_process_gui, plot_gui)) \
        .grid(row=1, column=7, sticky=W)

    Button(feature_panel,
           text='cgm_fft',
           command=lambda: cgm_fft(data_process_gui, plot_gui)) \
        .grid(row=1, column=8, sticky=W)

    Button(feature_panel,
           text='Macro 5',
           command=lambda: macro_5(data_process_gui, plot_gui)) \
        .grid(row=1, column=9, sticky=W)

    root.mainloop()
