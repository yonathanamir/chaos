# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 10:05:57 2022

@author: Yonathan
"""
from datetime import datetime

mpl.rcParams.update(mpl.rcParamsDefault)
mpl.rcParams['lines.markersize'] = 1

COLOR_LIST = ['r', 'b']

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
t1 = datetime.now()
am_files = glob.glob(r"C:\University\Semester G\Lab B2\Week 5\*\*.csv")
for i, f in enumerate(am_files):
    it = (c for c in COLOR_LIST)
    plt.clf()
    
    cols = [4,10]
    if 'to' in f:
        cols.append(16)
    
    datas = read_modulated_data(f, win_size=4000, limit=1, offset=0, cols=cols)

    for d in datas:
        color = next(it)
        bi_map = plot_bi_map(d, c=color, show=False, marker='.', prominence=1)
        bifurcations = find_bifurcations(bi_map, threshold=0.5)
                
        for v in bifurcations:
            if v[1] < 4:
                plt.axvline(x=v[0], color=color, alpha=0.3)
        
    title = ' '.join(f.split('\\')[-2:])
    plt.title(title)
    plt.xlim(0, 10000)
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

datas = read_modulated_data(am_file, win_size=4000, limit=1, offset=0, cols=[4, 10])
bi_map = gen_bi_plot_data(datas[0], prominence=1)

plt.scatter(bi_map[:,0], bi_map[:,1], color='b')

bifurcations = find_bifurcations(bi_map)
        
for v in bifurcations:
    # if v[1] > 1:
    plt.axvline(x=v[0], color='b', alpha=0.3)

plt.show()


print('Done!')
