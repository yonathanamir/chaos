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
    parser.add_argument('--marker-size', type=int, default=1)
    parser.add_argument('--ylim', type=int, default=15)

    parser.add_argument('--window-size', type=int, default=2000)
    parser.add_argument('--window-pad', type=float, default=0.1)

    parser.add_argument('--limit', type=float, default=1.0)
    parser.add_argument('--offset', type=float, default=0)
    parser.add_argument('--stride', type=float, default=1.0)

    parser.add_argument('--v_-in', type=float, default=0.0)
    parser.add_argument('--v-max', type=float, default=10.0)
    parser.add_argument('--v-step', type=float, default=0.01)

    parser.add_argument('--freq-sweep', action='store_true')
    parser.add_argument('--freq-min', type=float, default=10000.0)
    parser.add_argument('--freq-max', type=float, default=40000.0)
    parser.add_argument('--freq-step', type=float, default=1000.0)
    
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

    ax.set_ylim([0, args.ylim])
    ax.set_ylabel("Diode Voltage")
    
    mpl.rcParams['lines.markersize'] = args.marker_size

    data_fetcher = ScopeDataFetcher(args.scope_visa_address, args.channels_to_sample)
    awg = AwgDevice(visa_address=args.awg_visa_adress)

    if not args.freq_sweep:
        scatters = []
        for i in range(args.channels_to_sample):
            scatters.append(ax.scatter([], [], c=COLOR_MAP[i], marker=args.marker))

    # TODO: get from scope
    time_length_secs = 0.1 # in seconds
    total_pixel_length = 10**6
    input_am_frequency = 25 * 10 ** 3 # in Hz
    sample_win_size = calculate_sample_win_size(time_length_secs, total_pixel_length, input_am_frequency)

    while True:
        try:
            def v_sweep(freq=None):
                for v in range(args.v_min, args.v_max, args.v_step):
                    awg.voltage = v

                    for j in range(args.samples_per_voltage):
                        input_v, datas = data_fetcher.get_data()
                        for i in range(args.channels_to_sample):
                            peaks = chaosv2.max_val_window_peaks(datas[i], sample_win_size, window_pad=args.window_pad)

                            if args.freq_sweep:
                                ax.set_offsets(np.c_[
                                                            v * np.ones(len(peaks)),
                                                            peaks,
                                                            freq * np.ones(len(peaks))
                                                        ])
                                fig.canvas.draw()
                                fig.canvas.flush_events()
                            else:
                                scatters[i].set_offsets(np.c_[v*np.ones(len(peaks)), peaks])
                                fig.canvas.draw()
                                fig.canvas.flush_events()

            if args.freq_sweep:
                for freq in range(args.freq_min, args.freq_max, args.freq_step):
                    awg.frequency = freq
                    v_sweep()
            else:
                v_sweep()

        except Exception as ex:
            print(ex)
            print('Error getting data, sleeping for 5 sec...')
            time.sleep(5)
            os.system('cls')


if __name__ == '__main__':
    import sys
    
    args = init_args(sys.argv[1:])
    do_main(args)
    