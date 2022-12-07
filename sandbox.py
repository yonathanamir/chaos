# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 10:05:57 2022

@author: Yonathan
"""
from datetime import datetime

mpl.rcParams.update(mpl.rcParamsDefault)
mpl.rcParams['lines.markersize'] = 1

COLOR_LIST = ['r', 'b', 'g', 'orange']

#%% Single
am_file = r"C:\University\Semester G\Lab B2\Week 3\parallel.csv"
# am_file = r"C:\University\Semester G\Lab B2\Week 4\singles\a\a-ramp-1.csv"

datas = read_modulated_data(am_file, win_size=20, limit=1, offset=0, cols=[4, 10])

plot_bi_map(datas, c='r', show=False, marker='.')

plt.show()

print('Done!')

#%% Folder
import os
import glob

time_length_secs = 0.1 # in seconds
total_pixel_length = 10**6
input_am_frequency = 25 * 10 ** 3 # in Hz
sample_win_size = calculate_sample_win_size(time_length_secs, total_pixel_length, input_am_frequency)

t1 = datetime.now()
am_files = glob.glob(r"C:\University\Semester G\Lab B2\Week 6\single\b*.csv")
for i, f in enumerate(am_files):
    it = (c for c in COLOR_LIST)
    plt.clf()
    
    if 'cascade' in f:
        cols = [4,10,16,22]
    
    if 'single' in f:
        cols = [4,10]
    
    if 'parallel' in f:
        cols = [4,10,16,22]
    
    if 'overload' in f:
        cols = [4,10,16,22]
        
    
    datas = read_modulated_data(f, win_size=sample_win_size, limit=1, offset=0, cols=cols)

    for i in range(2):
        for d in datas:
            color = next(it)
            if i == 0:
                method='find_peaks'
                bi_map = plot_bi_map(d, c=color, show=False, marker='.', prominence=1)
            else:
                method='max_val'
                bi_map = plot_bi_map(d, c=color, show=False, marker='.', win_size=sample_win_size)
            # bifurcations = find_bifurcations(bi_map, threshold=0.5, back_window=5)
                    
            # for v in bifurcations:
            #     if v[1] < 4:
            #         plt.axvline(x=v[0], color=color, alpha=0.1)
            
        title = ' '.join(f.split('\\')[-2:])
        plt.title(title)
        plt.xlim(0, 11000)
        plt.ylim(0, 30)
    
        plt.show()
    # plt.savefig(f'{f}.png')
t2 = datetime.now()
print(f'Done! {t2-t1}')

#%% prominence
t1 = datetime.now()
file = r"C:\University\Semester G\Lab B2\Week 4.1\a\\a-22-mH.csv"
for i in range(0, 8):
    win_size = int(2 * (10 ** ((i/2)+2)))
    print(f'Win: {win_size}')
    plt.clf()
    
    datas = read_modulated_data(file, win_size=win_size, limit=1, offset=0, cols=[4, 10], do_print=False)

    plot_bi_map(datas[0], c='r', show=False, marker='.', prominence=1, do_print=False)
    # plt.xlim(0, 11000)
    # plt.ylim(0, 18)
    plt.title(os.path.basename(f))

    plt.show()
t2 = datetime.now()
print(f'Done! {t2-t1}')

#%% Bifurcation detection tests
am_file = r"C:\University\Semester G\Lab B2\Week 5\symmetric no chaos\b.csv"

datas = read_modulated_data(am_file, win_size=2000, limit=1, offset=0, cols=[4, 10])
bi_map = gen_bi_plot_data(datas[0], prominence=1)

plt.scatter(bi_map[:,0], bi_map[:,1], color='b')

bifurcations = find_bifurcations(bi_map, back_window=1)
        
for v in bifurcations:
    plt.axvline(x=v[0], color='b', alpha=0.3)

plt.show()


print('Done!')

#%% Max peak detection
am_file = r"C:\University\Semester G\Lab B2\Week 6\single\b-5.csv"

cols = [4, 10]
cols_data = read_data(am_file, col=cols, do_print=False)
input_v = cols_data[0]
measured_data = cols_data[1:]

time_length_secs = 0.1 # in seconds
total_pixel_length = 10**6
input_am_frequency = 25 * 10 ** 3 # in Hz
sample_win_size = calculate_sample_win_size(time_length_secs, total_pixel_length, input_am_frequency)

datas = read_modulated_data(am_file, win_size=sample_win_size)
bi_map = gen_bi_plot_data(datas[0], win_size=sample_win_size)
# bi_map = gen_bi_plot_data(datas[0], prominence=1)

plt.scatter(bi_map[:,0], bi_map[:,1], color='r')

plt.show()


print('Done!')
