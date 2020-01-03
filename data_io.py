import pandas as pd
import os
from data_process import currents_to_glucose, load_cgm_data, compute_MARD, compute_MSE
import numpy as np
import matplotlib.pyplot as plt


def load_data_info(data_info_file, data_dir):
    info_dict_list = pd.read_excel(data_info_file, usecols="A,B,C,E,F,I,J", encoding='utf-8').to_dict('records')
    info_dict = list(filter(lambda info: (str(info['電極編號']) + '_' + str(info['傳感器編號'])) in data_dir, info_dict_list))[0]

    return info_dict


def get_data_filename(data_dir):
    cgm_data_file = data_dir + '/' + list(filter(lambda f: '_T' in f, os.listdir(data_dir)))[0]
    bgm_data_file = data_dir + '/' + list(filter(lambda f: f.startswith('bgm'), os.listdir(data_dir)))[0]

    return cgm_data_file, bgm_data_file


def load_data(cgm_data_file, bgm_data_file):
    cgm_data = load_cgm_data('electricCurrent0', filename=cgm_data_file)
    bgm_data = pd.read_csv(bgm_data_file, encoding='utf-8').to_dict('records')

    return cgm_data, bgm_data