import pandas as pd
import numpy as np
from pykalman import KalmanFilter

kf = KalmanFilter(transition_covariance=0.18, observation_covariance=1)


def load_cgm_data(col_name, df=None, filename=None):
    if df is None:
        df = pd.read_csv(filename, encoding='utf-8')

    indices = np.array(df['index'].to_list())
    col_datas = np.array(df[col_name].to_list())

    return np.append(np.zeros(int(indices[0])), col_datas)


def parse_data(data, in_num, testing_range=None):
    if testing_range is None:
        testing_range = [len(data), len(data)]
    x, y = np.array([]), np.array([])

    for i in range(len(data) - in_num):
        x = np.append(x, data[i:i + in_num])
        y = np.append(y, data[i + in_num])

    if in_num > 0:
        x = np.array(x).reshape(int(len(x) / in_num), in_num)

    return np.append(x[:testing_range[0]-in_num], x[testing_range[1]-in_num+1:], axis=0), \
           x[testing_range[0]-in_num:testing_range[1]-in_num+1], \
           np.append(y[:testing_range[0]-in_num], y[testing_range[1]-in_num+1:], axis=0), \
           y[testing_range[0]-in_num:testing_range[1]-in_num+1]


def min_max_normalize(data, data_min, data_max):
    return (data - data_min) / (data_max - data_min)


def normalize_inverse(data, data_min, data_max):
    return data * (data_max - data_min) + data_min


def window_means(data, n, shift):
    x = range(0, len(data), shift)
    return x, [np.array(data[i - n if i >= n else 0:i + 1]).mean() for i in x]


def window_medians(data, n, shift):
    x = range(0, len(data), shift)
    return x, [np.median(np.array(data[i - n if i >= n else 0:i + 1])) for i in x]


def currents_to_glucose(currents, a, b):
    return currents * a + b


def glucose_to_current(glucose, a, b):
    return (glucose - b) / a


def kalman_filter(measurements):
    (filtered_state_means, filtered_state_covariances) = kf.filter(measurements)

    return filtered_state_means


def find_steady(data):
    x, medians = window_medians(data, 720, 60)

    continue_decrease_count = 0
    continue_increase_count = 0
    increase_stop_count = 0

    for i in range(1, len(medians)):
        max_m = max(medians[:i])
        min_m = min(medians[2 if i>2 else 0:i])

        if continue_decrease_count < 5:
            if medians[i] < medians[i-1]:
                continue_decrease_count = continue_decrease_count + 1
            else:
                continue_decrease_count = 0
        elif continue_increase_count < 5:
            if medians[i] > medians[i-1]:
                continue_increase_count = continue_increase_count + 1
            else:
                continue_increase_count = 0
        elif increase_stop_count < 5:
            if medians[i] <= medians[i-1] and ((medians[i]-min_m) / (max_m-min_m)) > 0.5:
                increase_stop_count = increase_stop_count + 1
            else:
                increase_stop_count = 0
        else:
            return x[i]

    return x[len(medians)-1]


def linear_regression(x, y):
    x, y = np.array(x), np.array(y)
    a = ((x - x.mean()) * (y - y.mean())).sum() / ((x - x.mean()) * (x - x.mean())).sum()
    b = y.mean() - a * x.mean()
    return a, b


def compute_MARD(x, y, a, b):
    return np.abs((y - currents_to_glucose(x, a, b)) / y).sum() / len(y)


def compute_MSE(x, y, a, b):
    return np.square(y - currents_to_glucose(x, a, b)).mean()
