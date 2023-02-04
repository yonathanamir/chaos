# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 09:31:16 2022
RLD bifurcation data parsing and analysis.

@author: Yonathan
"""

import numpy as np
import csv
from scipy import signal


_cache = {}
_do_print = False


def calculate_sample_win_size(total_time_length, total_pixel_length, input_am_frequency):
    """
    Calculates the sample window size based on the total time length, total pixel length and input amplitude modulation
    frequency.

    Parameters
    ----------
    total_time_length : float
        Total time length of the experiment.

    total_pixel_length : int
        Total pixel length of the experiment.

    input_am_frequency : float
        Input amplitude modulation frequency.

    Returns
    ----------
    sample_window_size : int
        The calculated sample window size.

    """
    dt = total_time_length / total_pixel_length
    return int(1 / (input_am_frequency * dt))


def read_data(file, col, use_cache=True):
    """
    Reads data from a CSV file and returns the specified columns.
    
    Parameters
    ----------
    file : str)
        The file path.

    col : int or list of ints
        The columns to return.

    use_cache : bool, optional
        Whether to use a cache for the data (default is True).
    
    Returns
    ----------
    cols_data : list
        The data for each column.

    """
    if isinstance(col, int):
        col = [col]
    
    cache_key = (file, ','.join([str(x) for x in col]))
    if _do_print:
        print(f'Cache key: {cache_key}')
    if use_cache and cache_key in _cache:
        if _do_print:
            print(f'Cache hit for {cache_key}!')
        return _cache[cache_key]
    
    filedata = []
        
    for _ in col:
        filedata.append([])
        
    if _do_print:
        print(f'Opening {file}')
    with open(file) as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            for j, c in enumerate(col):
                filedata[j].append(float(row[c]))
    
    if len(filedata) == 1:
        _cache[cache_key] = filedata[0]
    else:
        _cache[cache_key] = tuple(filedata)
        
    return _cache[cache_key]


def bi_data_from_am_data_single_window(input_v, measured_data, win_size, win_pad=0, peaks_method=None, *args, **kwargs):
    """
    The function outputs a list of dictionaries, with each dictionary representing the measured data at each frequency.
    Each dictionary maps the maximum voltage in a window to a list of peak values in that window.

    The function divides the input_v into windows with size win_size and a padding of win_pad, and for each window it
    extracts the maximum voltage in the window and uses it as the key in the output dictionary. It then uses the
    peaks_method to extract peaks from the corresponding section of each measured_data and adds these peaks to the list
    in the output dictionary for the current window's maximum voltage.

    The offsets variable is used to keep track of the starting index for each channel but is not implemented yet.

    Parameters
    ----------
    input_v : ndarray or list
        A 1-dimensional array, representing the input voltages.

    measured_data : ndarray or list
        A list of 1-dimensional arrays, representing the measured data from each channel.

    win_size : int
        The size of the window.

    win_pad : float, optional
        The padding of the window (default value is 0).

    peaks_method : function, optional
        A method to extract peaks from a data set (default is extract_peaks_areas).

    Returns
    ----------
        peak_datas : dict
            A dictionary representing the peaks for each voltage, for each channel. Use flatten_peak_data to turn this
            object into xs and ys lists for scatter plot.
    """
    results = []
    for _ in measured_data:
        results.append({})

    if peaks_method is None:
        peaks_method = extract_peaks_areas

    offsets = np.zeros(len(measured_data), int)  # TODO: Auto detect offsets for first peaks
        
    for j, data in enumerate(measured_data):
        for i in range(offsets[j], len(input_v), win_size):
            min_i = max(0, int(i-(win_size*win_pad)))
            max_i = min(len(input_v), int(i+(1+win_pad)*win_size))
            
            v = max(np.abs(input_v[min_i:max_i]))
            if v not in results[j]:
                results[j][v] = []
                
            sub_data = data[min_i:max_i]
            peaks, indices = peaks_method(sub_data, *args, **kwargs)
            results[j][v] += [sub_data[i] for i in indices]
        
    return results


def bi_data_from_am_file_single_window(am_file, cols, *args, **kwargs):
    """
    Read AM file and return bi_data_from_am_data_single_window.
    """
    if _do_print:
        print(f'Reading modulated file {am_file} with dingle window.')
    cols_data = read_data(am_file, col=cols)
    input_v = cols_data[0]
    measured_data = cols_data[1:]

    return bi_data_from_am_data_single_window(input_v, measured_data, *args, **kwargs)


def flatten_peak_data(peak_data):
    """
    Flatten a peak_data dictionary into a scatter plot ready xs and ys lists.

    Takes as input a nested dictionary peak_data and returns two arrays, xs and ys containing the input voltages (values
    of the keys) and diode peak voltages (values in the dictionary,) respectively.

    The function starts by initializing an empty list vals. Then, it uses nested list comprehension to flatten the
    dictionary. The nested list comprehension iterates over the keys (input voltages) of peak_data, and for each key, it
    adds an array [voltage, peak] to the list, where peak is the value corresponding to the voltage key in peak_data.

    Finally, the function converts the resulting nested list to a numpy array res, and returns res[:,0] and res[:,1],
    which are the first (xs) and second (ys) columns of res, respectively.

    Returns
    ----------
        xs : ndarray
            asd

        ys : ndarray
            asdfas

    """
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
    

def extract_peaks_areas(data, prominence_epsilon=0.2, distance=100, zero_epsilon=0.01, fixed_window=False,
                        peak_window=10, normalize=False, *args, **kwargs):
    """
    Extracts the areas of peaks in a signal.

    This function finds the peaks in the input `data` array using the `scipy.signal.find_peaks` function.
    For each peak, the area under the curve is computed using the trapezoidal rule (`np.trapz`).
    The area of the peak is considered if it is greater than 0.

    Parameters
    -----------
    data: numpy.ndarray
        The input signal.

    prominence_epsilon: float, optional (default=0.2)
        The prominence value for the `scipy.signal.find_peaks` function, relative to the maximum value of the data.

    distance: int, optional (default=100)
        The distance value for the `scipy.signal.find_peaks` function.

    zero_epsilon: float, optional (default=0.01)
        The zero-threshold value for determining the extent of the peak, relative to the maximum value of the data.

    fixed_window: bool, optional (default=False)
        If True, the peak window is a fixed size equal to `peak_window` on both sides of the peak.
        If False, the window extends until the values in the signal drop below the `zero_epsilon` threshold.

    peak_window: int, optional (default=10)
        The size of the peak window for computation of the area, if `fixed_window` is True.

    normalize: bool, optional (default=False)
        If True, the areas of the peaks are normalized by `peak_window*2`.

    Returns
    --------
    numpy.ndarray, numpy.ndarray:
        The areas of the peaks and the indices of the peaks in the input `data`.

    """
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
        ret_peak_vals /= peak_window*2
    return ret_peak_vals, ret_peak_indices
    

def extract_peaks_prob(data, prominence_epsilon=0.2, peak_window=10, distance=100, *args, **kwargs):
    """
    Extracts the peaks in the input signal `data` using the `prominence` and `distance` parameters of the `find_peaks`
    function from the `scipy.signal` library. The `peak_window` parameter is used to define a sliding window around each
    peak, and the average of the signal within this window is calculated and returned as the `peak value`.

    Parameters
    ----------
    data : list or numpy.ndarray
        The input signal data.

    prominence_epsilon : float, optional
        The fraction of the maximum value of the `data` signal to be used as the `prominence` parameter for the
        `find_peaks` function. The default value is 0.2.

    peak_window : int, optional
        The size of the sliding window to be used around each peak. The default value is 10.

    distance : int, optional
        The `distance` parameter for the `find_peaks` function. The default value is 100.

    Returns
    -------
    numpy.ndarray, list
        A numpy array of peak values and a list of peak indices.

    """

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


def extract_peaks(data, prominence=0.5, win_size=None, *args, **kwargs):
    """
    extract_peaks is a method that extracts the peak values from a given input signal, x. The peaks are found using the
    find_peaks function from the signal library.
    The prominence argument sets the minimum prominence of a peak to be considered a peak. If win_size is not provided,
    the peaks are extracted from the whole signal. If win_size is provided, the signal is divided into windows of the
    given size, and peaks are extracted from each window.

    Parameters
    ----------
    data : list
        A 1D list of numeric values representing the input signal.

    prominence : float
        The minimum prominence of a peak to be considered a peak. Defaults to 0.5.

    win_size : int
        The size of the window to divide the signal into. If not provided, the whole signal is used.

    Returns
    ----------
    peak_vals : list
        A list of peak values, representing the y-value of the peaks.

    """
    if win_size is None:
        peak_indices = signal.find_peaks(data, prominence=prominence)[0]
        peak_vals = [data[i] for i in peak_indices]
    else:
        peak_vals = []
        for i in range(0, len(data), win_size):
            min_i = i
            max_i = i+win_size
            sub_data = data[min_i:max_i]

            peak_indices = signal.find_peaks(sub_data, prominence=prominence)[0]
            peak_vals += [sub_data[i] for i in peak_indices]

    return list(peak_vals)


# TODO: This method is a WIP and doesn't always work well.
def find_bifurcations(bi_map, threshold=1.0, back_window=1):
    """
    The find_bifurcations method performs the task of finding bifurcations in a bi-map data. The bi-map data is a 2D
    array, where each row represents the input voltage and the corresponding value of the diode voltage.

    The method starts by aggregating the data, joining all the diode voltages for a particular input voltage. It then
    calculates the number of bifurcations for each input voltage, by counting the number of jumps between adjacent diode
    voltages that are greater than the threshold. The number of bifurcations is calculated using the k-means clustering
    algorithm.

    Parameters
    ----------
    threshold : float
        Used to determine the  minimum difference between two adjacent diode voltages, which will be considered as a jump.

    back_window : int
        used to check the maximum number of rows before the current row, to determine if the current row is a
        bifurcation point or not.

    Returns
    ----------
    jump_voltages : list
        Returns the input voltages that correspond to the bifurcation points, which are defined as the rows where the
        number of bifurcations is greater than the maximum number of bifurcations in the back_window rows before the
        current row.

    """
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
    
    jump_voltages = [
        x[i,:] for i in range(1,x.shape[0])
        if x[i,1] > np.max(x[np.max([0,i-back_window]):i,1])
        ]
            
    return jump_voltages
