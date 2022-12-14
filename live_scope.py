# -*- coding: utf-8 -*-
"""
Created on Sun Nov 20 15:38:47 2022

@author: Yonathan
"""

import argparse
import time
import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from tabulate import tabulate
import os

from data_fetchers import DataFetcher, ScopeDataFetcher
from chaosv2 import analyze_am_signal, gen_bi_plot_data, find_bifurcations, calculate_sample_win_size


def init_args(args):
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--visa-address', type=str)
    parser.add_argument('--channels-to-sample', type=int, default=1)
    parser.add_argument('--target-fps', type=int, default=1)
    parser.add_argument('--test-mode', action='store_true')
    parser.add_argument('--show-bifs', action='store_true')
    
    parser.add_argument('--color', type=str, default='k')
    parser.add_argument('--marker', type=str, default='.')
    parser.add_argument('--marker-size', type=int, default=1)
    parser.add_argument('--xlim', type=int, default=10500)
    parser.add_argument('--ylim', type=int, default=10)
    parser.add_argument('--dynamic-xlim', action='store_true')
    parser.add_argument('--dynamic-ylim', action='store_true')
    
    parser.add_argument('--window-size', type=int, default=2000)
    parser.add_argument('--limit', type=float, default=1.0)
    parser.add_argument('--offset', type=float, default=0)
    parser.add_argument('--stride', type=float, default=1.0)
    
    return parser.parse_args(args)


COLOR_MAP = ['b', 'r', 'g', 'k', 'm']
# COLOR_MAP = ['k', 'k', 'k', 'k', 'k']

def add_random_noise(data):
    import random
    
    for i in range(len(data)):
        for j in range(len(data[i])):
            data[i][j] += (0.5 - random.random())
    
    return data

def print_time_table(t1,t2,t3,t4,t5):
    os.system('cls')
    headers = ['Stage', 'Time']
    table = [
        ['Fetch', t2-t1],
        ['AM Analysis', t3-t2],
        ['Bi Plot Gen', t4-t3],
        ['Plot', t5-t4],
        ['Step Total', t5-t1],
        ['','']
    ]
    
    print(tabulate(table, headers=headers))

def do_main(args):
    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    ax.set_xlim([0, args.xlim])
    ax.set_ylim([0, args.ylim])
    
    mpl.rcParams['lines.markersize'] = args.marker_size
    
    data_fetcher = DataFetcher()
    if not args.test_mode:
        data_fetcher = ScopeDataFetcher(args.visa_address, args.channels_to_sample)
      
    scatters = []
    for i in range(args.channels_to_sample):
        scatters.append(ax.scatter([], [], c=COLOR_MAP[i], marker=args.marker))
        
    axvs = []
    while True:
        try:
            t1 = datetime.now()
            input_v, datas = data_fetcher.get_data()
            t2 = datetime.now()
            
            time_length_secs = 0.1 # in seconds
            total_pixel_length = 10**6
            input_am_frequency = 25 * 10 ** 3 # in Hz
            sample_win_size = calculate_sample_win_size(time_length_secs, total_pixel_length, input_am_frequency)
            
            if args.test_mode:
                import copy
                datas = add_random_noise(copy.deepcopy(datas))

            analyzed = analyze_am_signal(input_v, datas, win_size=args.window_size, 
                                         limit=args.limit, offset=args.offset, 
                                         stride=args.stride, do_print=False)
            t3 = datetime.now()
            
            ymaxs = []
            for i, channel in enumerate(analyzed):

                if args.show_bifs:
                    for x in axvs:
                        x.remove()
                    axvs = []

                data = gen_bi_plot_data(channel, do_print=False, win_size=None)
                scatters[i].set_offsets(np.c_[data[:,0],data[:,1]])

                ymaxs.append(np.max(data[:,1]))

                if args.dynamic_xlim:
                    ax.set_xlim([np.min(np.abs(data[:,0])*0.9), np.max(np.abs(data[:,0]))*1.1])

                if args.show_bifs:
                    bifurcations = find_bifurcations(data, threshold=1)
                            
                    for v in bifurcations:
                        if v[1] < 4:
                            axvs.append(ax.axvline(x=v[0], color='k', alpha=0.1))
            
            if args.dynamic_ylim:
                ax.set_ylim([0, np.max(ymaxs)*1.1])

            t4 = datetime.now()
    
            
            fig.canvas.draw()
            fig.canvas.flush_events()
            
            t5 = datetime.now()
            # diff = t5 - t1
            # print(f'Step exec time: {diff}')
            # if diff < timedelta(seconds=args.target_fps):
            #     tosleep = diff.seconds
            #     print(f'Sleeping {tosleep} seconds...')
            #     time.sleep(tosleep)
            
            print_time_table(t1, t2, t3, t4, t5)
        except Exception as ex:
            print(ex)
            print('Error getting data, sleeping for 5 sec...')
            time.sleep(5)
            os.system('cls')

if __name__ == '__main__':
    import sys
    
    args = init_args(sys.argv[1:])
    do_main(args)
    