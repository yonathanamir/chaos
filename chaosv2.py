# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 09:31:16 2022

@author: Yonathan
"""

import numpy as np
import csv
import glob
import os

from scipy import signal
from matplotlib import pyplot as plt
import matplotlib as mpl

from time import sleep
from IPython.display import display, clear_output

#%%
_cache = {}

#%%
def read_data(file, col, end=None, use_cache=True, do_print=True):
    if isinstance(col, int):
        col = [col]
    
    cache_key = (file, ','.join([str(x) for x in col]))
    if do_print:
        print(f'Cache key: {cache_key}')
    if use_cache and cache_key in _cache:
        if do_print:
            print(f'Cache hit for {cache_key}!')
        return _cache[cache_key]
    
    filedata = []
        
    for c in col:
        filedata.append([])
        
    if do_print:
        print(f'Opening {file}')
    with open(file) as csvfile:
        reader = csv.reader(csvfile)
        if end is None:
            it = reader
        else:
            it = [r for i,r in enumerate(reader) if i <= end]
        for i, row in enumerate(reader):
            # print(f'Reading {i}')
            for j, c in enumerate(col):
                filedata[j].append(float(row[c]))
    
    if len(filedata) == 1:
        _cache[cache_key] = filedata[0]
    else:
        _cache[cache_key] = tuple(filedata)
        
    return _cache[cache_key]
    
def read_folder(path):
    data={}
    files = glob.glob(f'{path}/*.csv')
    files = [f for f in files if 'am' not in f]
    
    print(f'Reading {len(files)} files...')
    for file in files:
        m_volts = int(os.path.basename(file).split('.')[0])
        data.update({m_volts: read_data(file)})
        
        print(f'Reading {file}')

    print('')
    print('Done reading.')
    return data

def read_modulated_data(file, win_size, limit=1, offset=0, cols=[4, 10], stride=1, do_print=True):
    if do_print:
        print(f'Reading modulated file {file}')
    cols_data = read_data(file, col=cols, do_print=do_print)
    input_v = cols_data[0]
    measured_data = cols_data[1:]
    
    return analyze_am_signal(input_v, measured_data, win_size, limit, offset, stride, do_print=do_print)


def analyze_am_signal(input_voltage, measured_data, win_size, limit=1, 
                      offset=0, stride=1, do_print=True):
    if do_print:
        print('Analyzing AM signal.')
    data=[]
    for i in measured_data:
        data.append({})
    
    length=len(input_voltage)
    
    trace_offset = int(length*offset)
    trace_limit = int(length*limit)-int(win_size*stride)+trace_offset
        
    
    for i in range(trace_offset, trace_limit, int(win_size*stride)):
        if do_print:
            print(f'Step {i}')
        
        sub_i_v = input_voltage[i:i+win_size]
        
        voltage = int(np.max(np.abs(np.asarray(sub_i_v))) * 1000)
        
        for j, measurement in enumerate(measured_data):
            sub_array = measurement[i: i+win_size]
            if voltage in data[j]:  
                data[j][voltage] = np.append(data[j][voltage], sub_array)
            else:
                data[j].update({voltage: sub_array})
    if do_print:
        print(f'Done reading. Data length: {len(data[0])}')
    # if len(data) == 1:
    #     return data[0]
    
    return np.asarray(data)


def bi_data_from_am_file_single_window(am_file, cols, win_size, win_pad=0, 
                                       prominence_weight=0.1, epsilon_factor=0.02,
                                       do_print=True, 
                                       auto_offset=False):
    if do_print:
        print(f'Reading modulated file {am_file} - NEW!!!')
    cols_data = read_data(am_file, col=cols, do_print=do_print)
    input_v = cols_data[0]
    measured_data = cols_data[1:]
        
    return bi_data_from_am_data_single_window(input_v, measured_data, win_size, win_pad=win_pad, 
                                                prominence_weight=prominence_weight, epsilon_factor=epsilon_factor,
                                                do_print=do_print, 
                                                auto_offset=auto_offset)


def bi_data_from_am_data_single_window(input_v, measured_data, win_size, win_pad=0, 
                                       prominence_weight=0.1, epsilon_factor=0.02,
                                       do_print=True, 
                                       auto_offset=False):
    results = []
    for d in measured_data:
        results.append({})

    offsets = np.zeros(len(measured_data), int)
    if auto_offset:
        inner_window = 0.3
        for i, data in enumerate(measured_data):
            epsilon = np.array(data[0:win_size]).max() * epsilon_factor
            for j in range(0, win_size):
                sub_data = data[j:j+win_size]

                if np.all(sub_data[0:int(len(sub_data)*inner_window)] < epsilon) and \
                    np.all(sub_data[int(len(sub_data)*(1-inner_window)):len(sub_data)] < epsilon):
                    offsets[i] = j
                    break
        
    for j, data in enumerate(measured_data):
        epsilon = np.max(data) * epsilon_factor
        for i in range(offsets[j], len(input_v), win_size):
            min_i = max(0, int(i-(win_size*win_pad)))
            max_i = min(len(input_v), int(i+(1+win_pad)*win_size))
            
            v = max(np.abs(input_v[min_i:max_i]))
            if v not in results[j]:
                results[j][v] = []
                
            sub_data = data[min_i:max_i]

            # plt.plot(sub_data)
            # plt.ylim(-1,10)
            # plt.title(f"v={v},[{min_i}:{max_i}]")
            # plt.show()

            # prominence = prominence_weight*max(np.abs(sub_data))
            # peak_indices = signal.find_peaks(sub_data, prominence=prominence)[0]
            # results[j][v] += [sub_data[i] for i in peak_indices]
            
            peak = np.max(sub_data)
            if peak > epsilon:
                results[j][v] += [peak]
        
    return results


def flatten_peak_data(peak_data):
    vals = []
    for x in np.asarray([
     [[voltage, peak] for peak in peak_data[voltage]]
     for voltage in peak_data.keys()
     ], dtype=object):
        if x != []:
            for y in x:
                vals.append(y)
    res = np.array(vals)
    return res[:,0], res[:,1]
                


def multiprocess_analyzer_am_signal(input_voltage, measured_data, 
                                    win_size, limit=1, offset=0, stride=1, 
                                    do_print=True, max_workers=1):
    import concurrent.futures
    
    data_length = len(input_voltage)
    index_map = [int(data_length*i/max_workers) for i in range(max_workers+1)]
    
    exec_results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_data = {
                executor.submit(analyze_am_signal, 
                                input_voltage[index_map[i]: index_map[i+1]],
                                measured_data[:, index_map[i]: index_map[i+1]],
                                win_size, limit, offset, stride, False): i
                for i in range(max_workers)
            }
        
        for future in concurrent.futures.as_completed(future_to_data):
            data = future_to_data[future]
            res = future.result()
            exec_results[data] = res
            
    final = [{} for i in range(measured_data.shape[0])]
    for worker in exec_results:
        for i, val in enumerate(exec_results[worker]):
            for voltage in val:
                if voltage in final[i]:
                    final[i][voltage] = np.append(final[i][voltage], val[voltage])
                else:
                    final[i][voltage] = val[voltage]
            
    return final
    

def extract_peaks_areas(data, prominence_epsilon=0.2, distance=100, zero_epsilon=0.01, fixed_window=False, peak_window=10, normalize=False):
    ret_peak_vals = []
    ret_peak_indices = []

    maxval = np.max(data)
    prom = maxval*prominence_epsilon
    zero = maxval*zero_epsilon

    peak_indices, _ = signal.find_peaks(data, prominence=prom, distance=distance)
    for peak_i in peak_indices:
        left = max(0, peak_i-peak_window)
        right = min(len(data), peak_i+peak_window)

        if not fixed_window:
            for i in range(peak_i-1, max(0, peak_i-peak_window), -1):
                if data[i] < zero:
                    left = i
                    break
                
            for i in range(peak_i+1, min(len(data), peak_i+peak_window), 1):
                if data[i] < zero:
                    right = i
                    break

        area_peak = np.trapz(data[left:right])

        if area_peak > 0:
            ret_peak_indices += [peak_i]
            ret_peak_vals += [area_peak]
    ret_peak_vals = np.array(ret_peak_vals)
    if normalize:
        # ret_peak_vals *= maxval / np.max(ret_peak_vals)
        ret_peak_vals /= peak_window*2
    return ret_peak_vals, ret_peak_indices
    

def extract_peaks_prob(data, prominence_epsilon=0.2, peak_window=10, distance=100):
    ret_peak_vals = []
    ret_peak_indices = []
    prom = np.max(data)*prominence_epsilon
    peak_indices, _ = signal.find_peaks(data, prominence=prom, distance=distance)
    for peak_i in peak_indices:
        prob_peak = np.average(data[peak_i-peak_window:peak_i+peak_window])

        if prob_peak > 0:
            ret_peak_indices += [peak_i]
            ret_peak_vals += [prob_peak]

    return np.array(ret_peak_vals), ret_peak_indices


def extract_peaks(x, prominence=0.5, win_size = None):
    if win_size is None:
        peak_indices = signal.find_peaks(x, prominence=prominence)[0]
        peak_vals = [x[i] for i in peak_indices]
    else:
        peak_vals = []
        for i in range(0, len(x), win_size):
            # min_i = int(max(i-(window_pad*win_size), 0))
            # max_i = int(min(i+(1+window_pad)*win_size, len(data)))
            
            min_i = i
            max_i = i+win_size
            sub_data = x[min_i:max_i]

            peak_indices = signal.find_peaks(sub_data, prominence=prominence)[0]
            peak_vals += [sub_data[i] for i in peak_indices]

    return list(set(peak_vals))


def max_val_window_peaks(data, win_size, offset=0, _DEBUG=True,
                         window_pad = 0):
    peak_vals = []
    for i in range(offset, len(data), win_size):
        min_i = int(max(i-(window_pad*win_size), 0))
        max_i = int(min(i+(1+window_pad)*win_size, len(data)))
        
        # min_i = i
        # max_i = i+win_size
    
        peak_vals.append(np.max(data[min_i:max_i]))
        if _DEBUG:
            d = data[i:i+win_size]; 
            plt.plot(np.arange(d.shape[0]), d); 
            plt.title(i); 
            plt.show();
    
    return np.unique(np.around(peak_vals, 3))

def plot_bi_map(data, c='k', marker='.', show=True, label=None, prominence=0.5,
                do_print=True, win_size=None, window_pad = 0,use_find_peaks = False):        
    vals = gen_bi_plot_data(data, prominence=prominence, do_print=do_print, 
                            win_size=win_size, window_pad = window_pad,
                            use_find_peaks = use_find_peaks)
    
    if do_print:
        print(f'Plotting...')
    plt.scatter(vals[:,0]/1000, vals[:,1], c=c, marker=marker, label=label)

    plt.xlabel('Input Voltage (V)')
    plt.ylabel('Diode Voltage values (V)')
    if show:
        plt.show()

    if do_print:
        print('Done plotting.')
    return vals

def gen_bi_plot_data(data, do_print=True, prominence=1, use_find_peaks = False,
                     win_size=None, window_pad = 0):
    if do_print:
        print('Finding peaks...')
    peak_data = {}
    for voltage in data.keys():
        if use_find_peaks:    # signal find_peaks algorithm
            peaks = extract_peaks(data[voltage], prominence=prominence, win_size=win_size)
        else:   # Max-val window peak search
            # debug = voltage // 1000 == 3
            debug=False
            
            if debug:    
                plt.plot(np.arange(data[voltage].shape[0]), data[voltage]); 
                plt.title(f'Voltage {voltage}'); 
                plt.show();
            peaks = max_val_window_peaks(data[voltage], win_size=win_size, 
                                         _DEBUG=False, window_pad=window_pad)
        peak_data.update({voltage: peaks})
        if do_print:
            print(f'Found {len(peak_data[voltage])} peaks for {voltage} mV')
    if do_print:
        print('')
        print('Done peak search.')
 
    vals = []
    for x in np.asarray([
     [[voltage, peak] for peak in peak_data[voltage]]
     for voltage in peak_data.keys()
     ], dtype=object):
        if x != []:
            for y in x:
                vals.append(y)
                
    return np.asarray(vals)

def plot_zooms(data, filters, legend_mapping, prefix=None, marker='.'):
    colors = legend_mapping[0]
    for j, f in enumerate(filters):
        print(f'Plotting {f[0]}-{f[1]}')
        legend_loc = None
        if isinstance(f, tuple):
            legend_loc = f[1]
            f = f[0]

        for i in [0,1]:
            filtered_keys = [k for k in data[i].keys() if f[0] <= k <= f[1]]
            filtered = {}
            for k in filtered_keys:
                filtered[k] = data[i][k]

            mpl.rcParams['lines.markersize'] = 4
            plot_bi_map(filtered, c=colors[i], show=False, marker=marker)

#         plt.title(f'{prefix}section {chr(j+65)} ({f[0]}-{f[1]} mV)')
        plt.title(f'{prefix}section {j+1} ({f[0]}-{f[1]} mV)')
        plt.show()

def find_bifurcations(bi_map, threshold = 1, back_window=1):
    from scipy import cluster

    # Aggregate data
    joined = {}
    for voltage, val in ((bi_map[i,0], bi_map[i,1]) for i in range(bi_map.shape[0]) ):
        if voltage not in joined:
            joined[voltage] = []
        joined[voltage].append(val)

    voltages = np.sort([v for v in joined.keys()])
        
    # Calculate clusters
    x = np.ones((len(voltages), 2))
    for i, voltage in enumerate(voltages):
        vals = np.sort(joined[voltage])
        jumps = np.array([vals[i+1]-vals[i] for i in range(vals.shape[0]-1)])
        jump_count = np.count_nonzero(jumps > threshold)
        bi_nums = jump_count+1

        if bi_nums < 8:
            try:
                clustered, _ = cluster.vq.kmeans(vals, bi_nums)
                x[i,:] = [voltage, clustered.shape[0]]
            except:
                x[i,:] = [voltage, 0]
        else:
            x[i,:] = [voltage, 0]

    # jump_voltages = [
    #     (np.min([y[0] for y in x if y[1]==a]), a) 
    #     for a in np.unique(x[:,1])
    #     if a > 1
    #     ]
    
    jump_voltages = [
        x[i,:] for i in range(1,x.shape[0])
        if x[i,1] > np.max(x[np.max([0,i-back_window]):i,1])
        ]
            
    return jump_voltages

def calculate_sample_win_size(total_time_length, total_pixel_length, input_am_frequency):
    dt = total_time_length / total_pixel_length
    return int(1 / (input_am_frequency * dt))
