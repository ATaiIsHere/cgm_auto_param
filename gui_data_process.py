from tkinter import *
from tkinter import ttk
import tkinter.filedialog
import traceback
import os
import numpy as np

import data_io
import data_process



class DataProcessGUI(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)

        self.label_data_dir = ttk.Label(self)
        self.label_data_dir['text'] = 'Data Path: '
        self.label_data_dir.grid(row=0, column=0, padx=5, pady=5, sticky=E)
        self.entry_data_dir = ttk.Entry(self)
        self.entry_data_dir['width'] = 60
        self.entry_data_dir.bind('<Button-1>', self.select_directory)
        self.entry_data_dir.insert(0, '/Users/sean.tai/PycharmProjects/cgm_auto_param/T11Data/3-6_T2310EED0196')
        self.entry_data_dir.grid(row=0, column=1, padx=5, pady=5, sticky=W)

        self.label_data_info_file = ttk.Label(self)
        self.label_data_info_file['text'] = 'Data Info File: '
        self.label_data_info_file.grid(row=1, column=0, padx=5, pady=5, sticky=E)
        self.entry_data_info_file = ttk.Entry(self)
        self.entry_data_info_file['width'] = 60
        self.entry_data_info_file.bind('<Button-1>', self.select_file)
        self.entry_data_info_file.insert(0, '/Users/sean.tai/PycharmProjects/cgm_auto_param/T11Data/T11公式.xlsx')
        self.entry_data_info_file.grid(row=1, column=1, padx=5, pady=5, sticky=W)

        self.btn_load_data_info = ttk.Button(self)
        self.btn_load_data_info['text'] = 'Load Data Info'
        self.btn_load_data_info['command'] = lambda: self.load_data_info(self.entry_data_info_file.get(),
                                                                         self.entry_data_dir.get())
        self.btn_load_data_info.grid(row=3, column=0)
        self.label_load_data_info_status = ttk.Label(self)
        self.label_load_data_info_status['text'] = ''
        self.label_load_data_info_status.grid(row=3, column=1, sticky=W)

        self.label_cgm_data_file = ttk.Label(self)
        self.label_cgm_data_file['text'] = 'CGM Data File:'
        self.label_cgm_data_file.grid(row=4, column=0, sticky=E)
        self.label_cgm_data_filename = ttk.Label(self)
        self.label_cgm_data_filename['text'] = ''
        self.label_cgm_data_filename.grid(row=4, column=1, sticky=W)

        self.label_bgm_data_file = ttk.Label(self)
        self.label_bgm_data_file['text'] = 'CGM Data File:'
        self.label_bgm_data_file.grid(row=5, column=0, sticky=E)
        self.label_bgm_data_filename = ttk.Label(self)
        self.label_bgm_data_filename['text'] = ''
        self.label_bgm_data_filename.grid(row=5, column=1, sticky=W)

        self.label_slope = ttk.Label(self)
        self.label_slope['text'] = 'Slope:'
        self.label_slope.grid(row=6, column=0, sticky=E)
        self.label_slope_val = ttk.Label(self)
        self.label_slope_val['text'] = ''
        self.label_slope_val.grid(row=6, column=1, sticky=W)

        self.label_intercept = ttk.Label(self)
        self.label_intercept['text'] = 'Intercept:'
        self.label_intercept.grid(row=7, column=0, sticky=E)
        self.label_intercept_val = ttk.Label(self)
        self.label_intercept_val['text'] = ''
        self.label_intercept_val.grid(row=7, column=1, sticky=W)

        self.info_dict = {}
        self.bgm_data = {}
        self.cgm_data = {}

    def select_directory(self, event):
        event.widget.delete(0, END)
        event.widget.insert(0, tkinter.filedialog.askdirectory(initialdir=os.getcwd()))

    def select_file(self, event):
        event.widget.delete(0, END)
        event.widget.insert(0, tkinter.filedialog.askopenfilename(initialdir=os.getcwd()))

    def load_data_info(self):
        data_info_file = self.entry_data_info_file.get()
        data_dir = self.entry_data_dir.get()
        print('load_data_info.data_info_file:', data_info_file)
        print('load_data_info.data_dir:', data_dir)
        try:
            self.info_dict = data_io.load_data_info(data_info_file, data_dir)
            cgm_data_file, bgm_data_file = data_io.get_data_filename(data_dir)
            self.label_cgm_data_filename['text'] = cgm_data_file
            self.label_bgm_data_filename['text'] = bgm_data_file
            self.load_data()
            self.label_slope_val['text'] = float(self.info_dict['斜率'])
            self.label_intercept_val['text'] = float(self.info_dict['截距'])
            self.label_load_data_info_status['text'] = 'Success'
        except:
            traceback.print_exc()
            self.label_load_data_info_status['text'] = 'Fail'

    def load_data(self):
        self.cgm_data, self.bgm_data = \
            data_io.load_data(self.label_cgm_data_filename['text'], self.label_bgm_data_filename['text'])

    def get_slope(self):
        return float(self.label_slope_val['text'])

    def get_intercept(self):
        return float(self.label_intercept_val['text'])

    def get_cgm_data(self, kalman=False):
        a = self.get_slope()
        b = self.get_intercept()
        data = data_process.kalman_filter(self.cgm_data) if kalman else self.cgm_data

        return range(len(data)), data_process.currents_to_glucose(data, a, b)

    def get_bgm_data(self):
        return [bgm['targetIndex'] for bgm in self.bgm_data], [bgm['mgdl'] for bgm in self.bgm_data]

    def get_steady_start(self):
        return int(self.info_dict['起'])

    def find_steady_start(self):
        return data_process.find_steady(self.cgm_data)

    def get_n_points_window_vals(self, n, shift, window_type='mean'):
        a = self.get_slope()
        b = self.get_intercept()
        data = data_process.currents_to_glucose(self.cgm_data, a, b)

        if window_type == 'mean':
            return data_process.window_means(data, n, shift)
        elif window_type == 'median':
            return data_process.window_medians(data, n, shift)
        else:
            return [], []


if __name__ == '__main__':
    root = Tk()
    root.title("Data Process GUI")

    app = DataProcessGUI(root)
    app.grid(row=0, column=0)

    root.mainloop()
