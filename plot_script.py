import pandas as pd
import os
from data_process import currents_to_glucose, load_cgm_data, compute_MARD, compute_MSE
import matplotlib.pyplot as plt

# Data Source parameter setting
root_dir = 'T11Data'
data_dir = root_dir + '/8-8_T2310EED0315'
data_info_file = root_dir + '/T11公式.xlsx'

# Plot parameter setting
# x_limit = [0, 8000]
x_limit = []
y_limit = [-200, 400]

# Load Data Info
info_dict_list = pd.read_excel(data_info_file, usecols="A,B,C,E,F,I,J", encoding='utf-8').to_dict('records')
info_dict = list(filter(lambda info: (str(info['電極編號']) + '_' + str(info['傳感器編號'])) in data_dir, info_dict_list))[0]

# Get CGM/BGM Filename
cgm_data_file = data_dir + '/' + list(filter(lambda f: '_T' in f, os.listdir(data_dir)))[0]
bgm_data_file = data_dir + '/' + list(filter(lambda f: f.startswith('bgm'), os.listdir(data_dir)))[0]

# Load CGM/BGM Data
bgm_data = pd.read_csv(bgm_data_file, encoding='utf-8').to_dict('records')
cgm_data = load_cgm_data('electricCurrent0', filename=cgm_data_file)

# slope, intercept setting
a = float(info_dict['斜率'])
b = float(info_dict['截距'])

# Plot
plt.plot(range(len(cgm_data)), currents_to_glucose(cgm_data, a, b), label="cgm")
plt.plot([bgm['targetIndex'] for bgm in bgm_data], [bgm['mgdl'] for bgm in bgm_data], marker='o', label="bgm")

if len(x_limit) > 0:
    plt.xlim(x_limit[0], x_limit[1])

if len(y_limit) > 0:
    plt.ylim(y_limit[0], y_limit[1])

plt.legend()
plt.show()
