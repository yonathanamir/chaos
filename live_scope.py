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
import json
import os

import chaosv2
from data_fetchers import ScopeDataFetcher
from awg_device import AwgDevice
from chaosv2 import calculate_sample_win_size


def init_args(args):
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--scope-visa-address', type=str)
    parser.add_argument('--awg-visa-address', type=str)
    parser.add_argument('--channels-to-sample', type=int, default=1)
    parser.add_argument('--samples-per-voltage', type=int, default=1)

    parser.add_argument('--color', type=str, default='k')
    parser.add_argument('--marker', type=str, default='.')
    parser.add_argument('--marker-size', type=float, default=1)
    parser.add_argument('--ylim', type=float, nargs=2, default=[0, 15])

    parser.add_argument('--window-size', type=int, default=2000)
    parser.add_argument('--window-pad', type=float, default=0.1)

    parser.add_argument('--limit', type=float, default=1.0)
    parser.add_argument('--offset', type=float, default=0)
    parser.add_argument('--stride', type=float, default=1.0)

    parser.add_argument('--v-min', type=float, default=0.1)
    parser.add_argument('--v-max', type=float, default=10.0)
    parser.add_argument('--v-num', type=int, default=100)

    parser.add_argument('--freq', type=float, default=25.0e3)
    parser.add_argument('--freq-sweep', action='store_true')
    parser.add_argument('--freq-min', type=float, default=10.0e3)
    parser.add_argument('--freq-max', type=float, default=40.0e3)
    parser.add_argument('--freq-num', type=int, default=100)
    
    parser.add_argument('--draw', action='store_true')
    parser.add_argument('--save', action='store_true')
    parser.add_argument('--save-path', type=str)
    
    return parser.parse_args(args)


COLOR_MAP = ['b', 'r', 'g', 'k', 'm']


def do_main(args):
    plt.ion()
    fig = plt.figure()

    if args.freq_sweep:
        ax = plt.axes(projection='3d')
        ax.set_zlim([args.freq_min, args.freq_max])
        ax.set_zlabel("AC Frequency (Hz)")
    else:
        ax = fig.add_subplot(111)

    ax.set_xlim([args.v_min, args.v_max])
    ax.set_xlabel("Input Voltage")

    ax.set_ylim(args.ylim)
    ax.set_ylabel("Diode Voltage")
    
    mpl.rcParams['lines.markersize'] = args.marker_size

    data_fetcher = ScopeDataFetcher(args.scope_visa_address, args.channels_to_sample, args.ylim)
    awg = AwgDevice(args.awg_visa_address)

    if not args.freq_sweep:
        scatters = []
        for i in range(args.channels_to_sample):
            scatters.append(ax.scatter([], [], c=COLOR_MAP[i], marker=args.marker))

    # TODO: get from scope
    time_length_secs = 4e-3 # in seconds
    total_pixel_length = 10**5
    input_am_frequency = 25 * 10 ** 3 # in Hz
    sample_win_size = calculate_sample_win_size(time_length_secs, total_pixel_length, input_am_frequency)

    all_peaks = {}
    while True:
        def v_sweep(freq=None):
            for v in np.linspace(args.v_min, args.v_max, args.v_num):
                awg.voltage = v
                if v not in all_peaks:
                    all_peaks[v] = []
                time.sleep(0.001)
                for j in range(args.samples_per_voltage):
                    input_v, datas = data_fetcher.get_data()
                    for i in range(0, len(datas)):
                        # peaks = chaosv2.max_val_window_peaks(datas[i], sample_win_size, window_pad=args.window_pad)
                        peaks = chaosv2.extract_peaks(datas[i], prominence=1)

                        all_peaks[v] += list(peaks)
                        if args.draw:
                            if args.freq_sweep:
                                pass
                                # ax.set_offsets(np.c_[
                                #                             v * np.ones(len(peaks)),
                                #                             peaks,
                                #                             freq * np.ones(len(peaks))
                                #                         ])
                                # fig.canvas.draw()
                                # fig.canvas.flush_events()
                            else:
                                xs = []
                                ys = []
                                for v in all_peaks.keys():
                                    xs += list(v*np.ones(len(all_peaks[v])))
                                    ys += all_peaks[v]
                                
                                ax.scatter(xs, ys, color='k')
                                # scatters[i].set_offsets(np.c_[v*np.ones(len(peaks)), peaks])
                                fig.canvas.draw()
                                fig.canvas.flush_events()
                                
                    if args.save:
                        if args.freq_sweep:
                            filename = os.path.join(args.save_path, f"freq-{freq}.json")
                            with open(filename, 'w') as f:
                                f.write(json.dumps(all_peaks))
                        else:
                            pass

        if args.freq_sweep:
            for freq in np.linspace(args.freq_min, args.freq_max, args.freq_num):
                awg.frequency = freq
                v_sweep(freq)   
        else:
            v_sweep(args.freq)

        # except Exception as ex:
        #     print(ex)
        #     print('Error getting data, sleeping for 5 sec...')
        #     time.sleep(5)
        #     os.system('cls')


if __name__ == '__main__':
    import sys
    
    args = init_args(sys.argv[1:])
    do_main(args)
    