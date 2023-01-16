# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 10:05:57 2022

@author: Yonathan
"""

#%% Init
from datetime import datetime
import numpy as np
import glob
import os

from matplotlib import pyplot as plt
import matplotlib as mpl

import chaosv2


mpl.rcParams.update(mpl.rcParamsDefault)
mpl.rcParams['lines.markersize'] = 1

COLOR_LIST = ['r', 'b', 'g', 'orange']
DIODES = ['A', 'B', 'C', 'D', 'E']

print("Done init.")

# %%

# %%

#%% New Single
am_file = r"C:\University\Semester G\Lab B2\Week 8\coupled\ab-control-100.csv"

time_length_secs = 0.1 # in seconds
total_pixel_length = 10**6
input_am_frequency = 25 * 10 ** 3 # in Hz
sample_win_size = chaosv2.calculate_sample_win_size(time_length_secs, total_pixel_length, input_am_frequency)

peak_datas = chaosv2.bi_data_from_am_file_single_window(am_file, cols=[4,10], 
                                                        win_size=sample_win_size, 
                                                        win_pad=0.0,
                                                        prominence_weight=0.1,
                                                        auto_offset=True,
                                                        do_print=False)
for i, d in enumerate(peak_datas):
    xs, ys = chaosv2.flatten_peak_data(d)
    plt.scatter(xs,ys, label=i)

lgnd = plt.legend()
for handle in lgnd.legendHandles:
    handle.set_sizes([10])

plt.show()

print('Done!')

#%% New Folder
import os
import glob

time_length_secs = 0.1 # in seconds
total_pixel_length = 10**6
input_am_frequency = 25 * 10 ** 3 # in Hz
sample_win_size = chaosv2.calculate_sample_win_size(time_length_secs, total_pixel_length, input_am_frequency)

t1 = datetime.now()
am_files = glob.glob(r"C:\University\Semester G\Lab B2\Week 8\*\*.csv")
for i, f in enumerate(am_files):
    plt.clf()
    
    if 'cascade' in f:
        cols = [4,10,16,22]
    
    elif 'single' in f:
        cols = [4,10]
    
    elif 'parallel' in f:
        cols = [4,10,16,22]
    
    elif 'overload' in f:
        cols = [4,10,16,22]
        
    elif 'controlled' in f:
        cols = [4,10,16]

    elif 'coupled' in f:
        cols = [4,10,16]
        
    elif '-to-' in f:
        cols = [4,10,16]

    elif 'assymetric' or 'symetric' in f:
        cols = [4,10]

    # peak_datas = chaosv2.bi_data_from_am_file_single_window(f, cols=cols, 
    #                                                         win_size=sample_win_size, 
    #                                                         win_pad=0.5,
    #                                                         prominence_weight=0.2,
    #                                                         do_print=False)

    peak_datas = chaosv2.bi_data_from_am_file_single_window(f, cols=cols, 
                                                            win_size=sample_win_size, 
                                                            win_pad=0,
                                                            prominence_weight=0.1,
                                                            # epsilon_factor=0.01,
                                                            auto_offset=True,
                                                            do_print=False)

    it = (c for c in COLOR_LIST)
    for i, d in enumerate(peak_datas):
        xs, ys = chaosv2.flatten_peak_data(d)
        
        mval = np.max(ys)
        color = next(it)
        
        plt.scatter(xs, ys, c=color, marker='.', label=f'Diode {DIODES[i]}')

        plt.xlabel('Input Voltage (V)')
        plt.ylabel('Diode Voltage values (V)')
        
    title = ' '.join(f.split('\\')[-2:])
    plt.title(title)
    plt.xlim(0, 11)
    plt.ylim(0, 30)
    
    lgnd = plt.legend()
    for handle in lgnd.legendHandles:
        handle.set_sizes([10])

    # plt.savefig(f'{f}.png')
    plt.show()
t2 = datetime.now()
print(f'Done! {t2-t1}')


# #%% Single
# am_file = r"C:\University\Semester G\Lab B2\Week 8\singles\c-control-000.csv"

# time_length_secs = 0.1 # in seconds
# total_pixel_length = 10**6
# input_am_frequency = 25 * 10 ** 3 # in Hz
# sample_win_size = chaosv2.calculate_sample_win_size(time_length_secs, total_pixel_length, input_am_frequency)

# datas = chaosv2.read_modulated_data(am_file, win_size=sample_win_size, limit=1, offset=0, cols=[4, 10])

# mval = max([max(vals) for vals in datas[0].values()])

# bi_map = chaosv2.plot_bi_map(datas[0], c='r', show=False, marker='.', win_size=sample_win_size,
#                      prominence=mval*0.02, use_find_peaks=True)

# # bi_map = plot_bi_map(d, c=color, show=False, marker='.', prominence=1)

# plt.show()

# print('Done!')

# #%% Folder
# import os
# import glob

# time_length_secs = 0.1 # in seconds
# total_pixel_length = 10**6
# input_am_frequency = 25 * 10 ** 3 # in Hz
# sample_win_size = chaosv2.calculate_sample_win_size(time_length_secs, total_pixel_length, input_am_frequency)

# t1 = datetime.now()
# am_files = glob.glob(r"C:\University\Semester G\Lab B2\Week 8\*\*.csv")
# for i, f in enumerate(am_files):
#     plt.clf()
    
#     if 'cascade' in f:
#         cols = [4,10,16,22]
    
#     if 'single' in f:
#         cols = [4,10]
    
#     if 'parallel' in f:
#         cols = [4,10,16,22]
    
#     if 'overload' in f:
#         cols = [4,10,16,22]
        
#     if 'controlled' in f:
#         cols = [4,10,16]

#     if 'coupled' in f:
#         cols = [4,10,16]


#     datas = chaosv2.read_modulated_data(f, win_size=sample_win_size, limit=1, offset=0, cols=cols)

#     for i in range(0,2):
#         it = (c for c in COLOR_LIST)
#         for d in datas:
#             mval = max([max(vals) for vals in d.values()])
#             color = next(it)
#             if i == 0:
#                 method='find_peaks'
#                 bi_map = chaosv2.plot_bi_map(d, c=color, show=False, marker='.', prominence=mval*0.02, use_find_peaks=True,
#                                              win_size=sample_win_size)
#             else:
#                 method='max_val'
#                 bi_map = chaosv2.plot_bi_map(d, c=color, show=False, marker='.',
#                                              win_size=sample_win_size, window_pad=0.1,
#                                              use_find_peaks=False)
#             # bifurcations = find_bifurcations(bi_map, threshold=0.5, back_window=5)
                    
#             # for v in bifurcations:
#             #     if v[1] < 4:
#             #         plt.axvline(x=v[0], color=color, alpha=0.1)
            
#         title = ' '.join(f.split('\\')[-2:] + [method])
#         plt.title(title)
#         plt.xlim(0, 11000)
#         plt.ylim(0, 30)
    
#         plt.show()
#     # plt.savefig(f'{f}.png')
# t2 = datetime.now()
# print(f'Done! {t2-t1}')

# #%% prominence
# t1 = datetime.now()
# file = r"C:\University\Semester G\Lab B2\Week 4.1\a\\a-22-mH.csv"
# for i in range(0, 8):
#     win_size = int(2 * (10 ** ((i/2)+2)))
#     print(f'Win: {win_size}')
#     plt.clf()
    
#     datas = read_modulated_data(file, win_size=win_size, limit=1, offset=0, cols=[4, 10], do_print=False)

#     plot_bi_map(datas[0], c='r', show=False, marker='.', prominence=1, do_print=False)
#     # plt.xlim(0, 11000)
#     # plt.ylim(0, 18)
#     plt.title(os.path.basename(f))

#     plt.show()
# t2 = datetime.now()
# print(f'Done! {t2-t1}')

# #%% Bifurcation detection tests
# am_file = r"C:\University\Semester G\Lab B2\Week 5\symmetric no chaos\b.csv"

# datas = read_modulated_data(am_file, win_size=2000, limit=1, offset=0, cols=[4, 10])
# bi_map = gen_bi_plot_data(datas[0], prominence=1)

# plt.scatter(bi_map[:,0], bi_map[:,1], color='b')

# bifurcations = find_bifurcations(bi_map, back_window=1)
        
# for v in bifurcations:
#     plt.axvline(x=v[0], color='b', alpha=0.3)

# plt.show()


# print('Done!')

# #%% Max peak detection
# am_file = r"C:\University\Semester G\Lab B2\Week 6\single\b-5.csv"

# cols = [4, 10]
# cols_data = read_data(am_file, col=cols, do_print=False)
# input_v = cols_data[0]
# measured_data = cols_data[1:]

# time_length_secs = 0.1 # in seconds
# total_pixel_length = 10**6
# input_am_frequency = 25 * 10 ** 3 # in Hz
# sample_win_size = calculate_sample_win_size(time_length_secs, total_pixel_length, input_am_frequency)

# datas = read_modulated_data(am_file, win_size=sample_win_size)
# bi_map = gen_bi_plot_data(datas[0], win_size=sample_win_size)
# # bi_map = gen_bi_plot_data(datas[0], prominence=1)

# plt.scatter(bi_map[:,0], bi_map[:,1], color='r')

# plt.show()


# print('Done!')

# %% Hi res
file = r"C:\University\Semester G\Lab B2\Week 8\coupled\bc-control-000.csv"

cols = [16]
cols_data = chaosv2.read_data(file, col=cols, do_print=False)
input_v = np.array(cols_data)

peaks, indices = chaosv2.extract_peaks_prob(input_v, peak_window=3, distance=50)

fixed = peaks + np.average(input_v[indices] - peaks)
orig_peaks = input_v[indices]

# plt.scatter(np.arange(len(indices)), peaks, label="prob peaks")
plt.scatter(np.arange(len(indices)), orig_peaks, label="original peaks")
# plt.scatter(np.arange(len(indices)), fixed, label="fixed prob")
plt.legend()

print(f'# of peaks: {len(indices)}')
print(f'Unique original peaks: {len(set(orig_peaks))}')
print(f'Unique fixed peaks: {len(set(fixed))}')
# %%
