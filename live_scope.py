# -*- coding: utf-8 -*-
"""
Created on Sun Nov 20 15:38:47 2022
Basic application for collecting and viewing RLD circuit birfurcation data.
Use --help flag for options, Check Readme.md for additional details.

@author: Yonathan
"""

import argparse
import time
import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
import json
import os
from scipy import signal
from datetime import datetime

import chaos
from data_fetchers import ScopeDataFetcher
from awg_device import AwgDevice
from chaos import calculate_sample_win_size


COLOR_MAP = ['b', 'r', 'g', 'k', 'm']


def init_args(args):
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--scope-visa-address', type=str,
                        help="Visa address of the oscilloscope device")
    parser.add_argument('--awg-visa-address', type=str,
                        help="Visa address of the AWG device")
    parser.add_argument('--channels-to-sample', type=int, default=1,
                        help="Number of channels to sample")
    parser.add_argument('--samples-per-voltage', type=int, default=1,
                        help="Number of samples per voltage")

    parser.add_argument('--marker', type=str, default='.',
                        help="Marker for plotting")
    parser.add_argument('--marker-size', type=float, default=1,
                        help="Size of the marker for plotting")
    parser.add_argument('--ylim', type=float, nargs=2, default=[0, 15],
                        help="Y-axis limits for plotting")

    parser.add_argument('--v-am', action="store_true",
                        help="Flag to use amplitude modulation instead of voltage sweep.")
    parser.add_argument('--v-min', type=float, default=0.1,
                        help="Minimum voltage for the sweep.")
    parser.add_argument('--v-max', type=float, default=10.0,
                        help="Maximum voltage for the sweep.")
    parser.add_argument('--v-num', type=int, default=100,
                        help="Number of voltage steps in the sweep.")
    parser.add_argument('--vs', nargs="+", type=float,
                        help="Explicit list of voltages to sweep instead of using min-max-steps.")

    parser.add_argument('--freq', type=float, default=25.0e3,
                        help="Frequency to use if not sweeping.")
    parser.add_argument('--freq-sweep', action='store_true',
                        help="Flag to perform frequency sweep")
    parser.add_argument('--freq-min', type=float, default=10.0e3,
                        help="Minimum frequency (in Hz) in the sweep.")
    parser.add_argument('--freq-max', type=float, default=40.0e3,
                        help="Maximum frequency (in Hz) in the sweep.")
    parser.add_argument('--freq-num', type=int, default=100,
                        help="Number of frequency steps in the sweep.")
    parser.add_argument('--freqs', nargs="+", type=float,
                        help="Explicit lst of frequencies to sweep instead of using min-max-steps.")

    parser.add_argument('--time-length-secs', type=float, default=1.0e-3,
                        help="Total length of the signal in seconds.")
    parser.add_argument('--total-pixel-length', type=float, default=10.0e3,
                        help="Total length of the signal in pixels (traces).")

    parser.add_argument('--peak-mode', type=str, default="area",
                        help="Mode for detecting peaks in the signal. Available options: are `normal`, `prob` and `area`.")
    parser.add_argument('--distance', type=int, default=50,
                        help="Distance threshold for detecting peaks (in pixels).")
    parser.add_argument('--peak-window', type=int, default=10,
                        help="Size of the window (in pixels) used for peak detection.")
    parser.add_argument('--prominence-epsilon', type=float, default=1/20,
                        help="Prominence epsilon for peak detection")
    
    parser.add_argument('--draw', action='store_true',
                        help="Plot the analyzed peak data as the program runs.")
    parser.add_argument('--save', action='store_true',
                        help="Save the results of each sweep to the save-path parameter.")
    parser.add_argument('--save-path', type=str,
                        help="Path to save to.")
    parser.add_argument('--loop', action='store_true',
                        help="After a full sweep, start another until Ctrl-C.")
    
    return parser.parse_args(args)


def do_main(args):
    plt.ion()
    fig = plt.figure()

    if args.freq_sweep:
        ax = plt.axes(projection='3d')

        if args.freqs:
            freq_lims = [min(args.freqs), max(args.freqs)]
        else:
            freq_lims = [args.freq_min, args.freq_max]
        ax.set_ylim(freq_lims)
        ax.set_ylabel("AC Frequency (Hz)")
        ax.set_zlim(args.ylim)
        ax.set_zlabel("Diode Voltage")
    else:
        ax = fig.add_subplot(111)
        ax.set_ylim(args.ylim)
        ax.set_ylabel("Diode Voltage")

    ax.set_xlim([args.v_min, args.v_max])
    ax.set_xlabel("Input Voltage")
    
    mpl.rcParams['lines.markersize'] = args.marker_size

    data_fetcher = ScopeDataFetcher(args.scope_visa_address, args.channels_to_sample)
    awg = AwgDevice(args.awg_visa_address)

    if not args.freq_sweep:
        scatters = []
        for i in range(args.channels_to_sample):
            scatters.append(ax.scatter([], [], c=COLOR_MAP[i], marker=args.marker))

    while True:
        def v_sweep(args, freq=None):
            if args.v_am:
                # TODO: get from scope?
                sample_win_size = calculate_sample_win_size(args.time_length_secs, args.total_pixel_length, freq)

                # TODO: Set AM voltage through AWG device
                awg.set_ramp(am_freq=10)

                input("Fix Trigger on oscilloscope and enter anything to continue.")
                time.sleep(0.5)
                input_v, datas = data_fetcher.get_data()

                peak_datas = chaos.bi_data_from_am_data_single_window(input_v, datas,
                                                        win_size=sample_win_size, 
                                                        win_pad=0.0,
                                                        prominence_weight=0.1,
                                                        auto_offset=False,
                                                        do_print=False)

                if args.draw:
                    for i, d in enumerate(peak_datas):
                        xs, ys = chaos.flatten_peak_data(d)

                        if args.freq_sweep:
                            zs = list(freq*np.ones(len(ys)))
                            ax.scatter(xs, zs, ys, color='k', s=args.marker_size)
                        else:
                            ax.scatter(xs, ys, color='k', s=args.marker_size, label=i)
                        fig.canvas.flush_events()
                        fig.canvas.draw()
                                
                    if args.save:
                        filename = os.path.join(args.save_path, f"freq-{int(freq)}.json")
                        with open(filename, 'w') as f:
                            f.write(json.dumps(peak_datas))                    

                return peak_datas

            all_peaks = {}
            awg.voltage = args.v_min
            print(f'Setting min v={args.v_min}')
            time.sleep(1)
            
            if args.vs:
                vs_list = np.array(args.vs)
            else:
                vs_list = np.linspace(args.v_min, args.v_max, args.v_num)
            for v in vs_list:
                awg.voltage = v
                print(f'Setting v={v}')
                if v not in all_peaks:
                    all_peaks[v] = []
                for j in range(args.samples_per_voltage):
                    _, datas = data_fetcher.get_data()                    

                    for i in range(0, len(datas)):
                        curr_max_v = np.max(datas[i])

                        if args.peak_mode == "normal":
                            peak_indices, _ = signal.find_peaks(datas[i], prominence=curr_max_v*args.prominence_epsilon, distance=args.distance)
                            peaks = list(np.unique([datas[i][index] for index in peak_indices]))
                        elif args.peak_mode == "prob":
                            peaks, indices = chaos.extract_peaks_prob(datas[i], peak_window=args.peak_window, distance=args.distance)

                            peaks = list(peaks)
                        elif args.peak_mode == "area":
                            peaks, indices = chaos.extract_peaks_areas(datas[i], peak_window=args.peak_window, distance=args.distance )

                            peaks = list(peaks)
                        else:
                            raise Exception("Bad peak mode!")

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
                                ax.scatter(xs, zs, ys, color='k', s=args.marker_size)
                            else:
                                ax.scatter(xs, ys, color='k', s=args.marker_size)
                            fig.canvas.flush_events()
                            fig.canvas.draw()
                                
                    # if args.save and not args.freq_sweep:
                    if args.save:
                        filename = os.path.join(args.save_path, f"freq-{int(freq)}.json")
                        with open(filename, 'w') as f:
                            f.write(json.dumps(all_peaks))

            return all_peaks

        t1 = datetime.now()
        if args.freq_sweep:
            all_freq = {}
            
            if args.freqs:
                freq_list = np.array(args.freqs)
            else:
                freq_list = np.linspace(args.freq_min, args.freq_max, args.freq_num)
            for freq in freq_list:
                try:
                    time.sleep(0.01)
                    awg.frequency = freq
                    print(f'Setting freq={freq}')
                    time.sleep(0.01)
                    freq_peaks = v_sweep(args, freq)
                    all_freq[freq] = freq_peaks
                except BaseException as e:
                    print(f"Sweep for f={freq} failed, skipping... Exception: {repr(e)}")
                    continue
        else:
            if args.freq:
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

        ax.cla()


if __name__ == '__main__':
    import sys
    
    args = init_args(sys.argv[1:])
    do_main(args)
    