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
import logging
import sys
from scipy import signal
from datetime import datetime, timedelta

import chaosv2
from data_fetchers import ScopeDataFetcher
from awg_device import AwgDevice
from chaosv2 import calculate_sample_win_size


# logger = logging.getLogger('chaos')
# logger.addHandler(logging.StreamHandler(sys.stdout))
# logger.info('hi')

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

    parser.add_argument('--prominence-epsilon', type=float, default=1/20)

    parser.add_argument('--v-min', type=float, default=0.1)
    parser.add_argument('--v-max', type=float, default=10.0)
    parser.add_argument('--v-num', type=int, default=100)

    parser.add_argument('--freq', type=float, default=25.0e3)
    parser.add_argument('--freq-sweep', action='store_true')
    parser.add_argument('--freq-min', type=float, default=10.0e3)
    parser.add_argument('--freq-max', type=float, default=40.0e3)
    parser.add_argument('--freq-num', type=int, default=100)

    parser.add_argument('--time_length_secs', type=float, default=10.0e3)
    parser.add_argument('--total-pixel_length', type=float, default=40.0e3)
    parser.add_argument('--input-am-frequency', type=int, default=100)

    parser.add_argument('--distance', type=int, default=50)
    parser.add_argument('--peak-window', type=int, default=3)
    
    # time_length_secs = 4e-3 # in seconds
    # total_pixel_length = 10**5
    # input_am_frequency = 25 * 10 ** 3 # in Hz
    
    parser.add_argument('--draw', action='store_true')
    parser.add_argument('--mesh', action='store_true')
    parser.add_argument('--save', action='store_true')
    parser.add_argument('--loop', action='store_true')
    parser.add_argument('--save-path', type=str)
    
    return parser.parse_args(args)


COLOR_MAP = ['b', 'r', 'g', 'k', 'm']


def do_main(args):
    print("hi")
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

    while True:
        def v_sweep(args, freq=None):

            if args.v_am:
                # TODO: get from scope?
                sample_win_size = calculate_sample_win_size(args.time_length_secs, args.total_pixel_length, args.input_am_frequency)

                # TODO: Set AM voltage through AWG device

                input("Fix Trigger on oscilloscope and enter anything to continue.")
                input_v, datas = data_fetcher.get_data()

                peak_datas = chaosv2.bi_data_from_am_data_single_window(input_v, datas, 
                                                        win_size=sample_win_size, 
                                                        win_pad=0.0,
                                                        prominence_weight=0.1,
                                                        auto_offset=True,
                                                        do_print=False)

                if args.draw:
                    for i, d in enumerate(peak_datas):
                        xs, ys = chaosv2.flatten_peak_data(d)

                        if args.freq_sweep:
                            zs += list(freq*np.ones(len(ys)))
                            ax.scatter(xs, ys, zs, color='k', s=args.marker_size)
                        else:
                            ax.scatter(xs, ys, color='k', s=args.marker_size, label=i)
                            fig.canvas.flush_events()
                        fig.canvas.draw()
                                
                    if args.save and not args.freq_sweep:
                        filename = os.path.join(args.save_path, f"freq-{int(freq)}.json")
                        with open(filename, 'w') as f:
                            f.write(json.dumps(peak_datas))                    

                return peak_datas

            # TODO: get from scope?
            sample_win_size = calculate_sample_win_size(args.time_length_secs, args.total_pixel_length, freq)

            all_peaks = {}
            awg.voltage = args.v_min
            print(f'Setting min v={args.v_min}')
            time.sleep(1)
            
            for v in np.linspace(args.v_min, args.v_max, args.v_num):
                awg.voltage = v
                print(f'Setting v={v}')
                if v not in all_peaks:
                    all_peaks[v] = []
                for j in range(args.samples_per_voltage):
                    _, datas = data_fetcher.get_data()                    

                    for i in range(0, len(datas)):
                        curr_max_v = np.max(datas[i])
                        # peaks = chaosv2.max_val_window_peaks(datas[i], sample_win_size, window_pad=args.window_pad)
                        # peaks = chaosv2.extract_peaks(datas[i], prominence=1)
                        # peak_indices, _ = signal.find_peaks(datas[i], prominence=curr_max_v*args.prominence_epsilon, distance=int(sample_win_size//2))
                        # peaks = list(np.unique([datas[i][index] for index in peak_indices]))

                        peaks, indices = chaosv2.extract_peaks_prob(datas[i], peak_window=args.distance, distance=args.distance)
                        fixed = peaks + np.average(np.array(datas[i][indices]) - peaks)
                        peaks = fixed

                        print(f'Found {len(peaks)} for freq={freq}, v={v}.')

                        all_peaks[v] += peaks
                        if args.draw:
                            xs = []
                            ys = []
                            zs = []
                            xs += list(v*np.ones(len(peaks)))
                            ys += peaks
                                
                            if args.freq_sweep:
                                zs += list(freq*np.ones(len(peaks)))
                                ax.scatter(xs, ys, zs, color='k', s=args.marker_size)
                            else:
                                ax.scatter(xs, ys, color='k', s=args.marker_size)
                                fig.canvas.flush_events()
                            fig.canvas.draw()
                                
                    if args.save and not args.freq_sweep:
                        filename = os.path.join(args.save_path, f"freq-{int(freq)}.json")
                        with open(filename, 'w') as f:
                            f.write(json.dumps(all_peaks))

            return all_peaks

        t1 = datetime.now()
        if args.freq_sweep:
            all_freq = {}
            for freq in np.linspace(args.freq_min, args.freq_max, args.freq_num):
                time.sleep(0.01)
                awg.frequency = freq
                print(f'Setting freq={freq}')
                time.sleep(0.01)
                freq_peaks = v_sweep(args, freq)
                all_freq[freq] = freq_peaks
        else:
            awg.frequency = args.freq
            v_sweep(args, args.freq)

        if args.save:
            plt.savefig(os.path.join(args.save_path, f"graph.png"))

            if args.freq_sweep:
                filename = os.path.join(args.save_path, f"run.json")
                with open(filename, 'w') as f:
                    f.write(json.dumps(all_freq))

        if not args.loop:
            t2 = datetime.now()
            input(f"Done sweep in {t2-t1}! Enter input to exit.")
            break

        # except Exception as ex:
        #     print(ex)
        #     print('Error getting data, sleeping for 5 sec...')
        #     time.sleep(5)
        #     os.system('cls')


if __name__ == '__main__':
    import sys
    
    args = init_args(sys.argv[1:])
    do_main(args)
    