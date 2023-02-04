import numpy as np
from matplotlib import pyplot as plt
import matplotlib as mpl

import chaosv2

mpl.rcParams.update(mpl.rcParamsDefault)
mpl.rcParams['lines.markersize'] = 1

COLOR_LIST = ['r', 'b', 'g', 'orange']
DIODES = ['A', 'B', 'C', 'D']

time_length_secs = 0.1  # in seconds
total_pixel_length = 10**6
input_am_frequency = 25 * 10 ** 3  # in Hz
sample_win_size = chaosv2.calculate_sample_win_size(time_length_secs, total_pixel_length, input_am_frequency)

print("Done init.")

# Single
single_file = r"C:\University\Semester G\Lab B2\chaos\testdata\single.csv"

peak_datas = chaosv2.bi_data_from_am_file_single_window(single_file, cols=[4,10], win_size=sample_win_size)
for i, d in enumerate(peak_datas):
    xs, ys = chaosv2.flatten_peak_data(d)
    plt.scatter(xs,ys, label=i, color='k', s=0.4, marker='.')

plt.xlabel('Input Voltage (V)')
plt.ylabel('Diode Voltage values (V)')
plt.show()

# Coupled
double_files = r"C:\University\Semester G\Lab B2\chaos\testdata\coupled.csv"
cols = [4, 10, 16]
peak_datas = chaosv2.bi_data_from_am_file_single_window(double_files, cols=cols, win_size=sample_win_size)

it = (c for c in COLOR_LIST)
for i, d in enumerate(peak_datas):
    xs, ys = chaosv2.flatten_peak_data(d)

    mval = np.max(ys)
    color = next(it)

    plt.scatter(xs, ys, c=color, marker='.', label=f'Diode {DIODES[i]}')

    plt.xlabel('Input Voltage (V)')
    plt.ylabel('Diode Voltage values (V)')

lgnd = plt.legend()
for handle in lgnd.legendHandles:
    handle.set_sizes([10])

plt.show()
print('Done!')
