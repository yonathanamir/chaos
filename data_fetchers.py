# -*- coding: utf-8 -*-
"""
Created on Sun Nov 20 17:39:19 2022

@author: Yonathan
"""

import pyvisa as visa # http://github.com/hgrecco/pyvisa
import time
import numpy as np

class DataFetcher:
    def __init__(self):
        self._data = None
    
    def get_data(self):
        if self._data is None:
            file = r"C:\Users\owner\Desktop\yonathan\week 3\parallel.csv"
            cols = [4, 10]
            
            from chaosv2 import read_data
            cols_data = read_data(file, col=cols)
            input_v = cols_data[0]
            measured_data = cols_data[1:]
            self._data = (np.asarray(input_v), np.asarray(measured_data))
        
        return self._data
        
class ScopeDataFetcher(DataFetcher):
    def __init__(self, visa_address, channels_to_sample):

        self.visa_address = visa_address
        self.channels_to_sample = channels_to_sample
        
        self.rm = visa.ResourceManager()
        self.scope = self.rm.open_resource(self.visa_address)
        self.scope.timeout = 10000 # ms
        self.scope.encoding = 'latin_1'
        self.scope.read_termination = '\n'
        self.scope.write_termination = None
        self.scope.write('*cls') # clear ESR
        
    def __del__(self):
        self.scope.close()
        self.rm.close()
        
    
    def get_data(self):
        input_v = self._sample_channel(1)
        measured_data = []
        for i in range(1, self.channels_to_sample, 1):
            measured_data.append(self._sample_channel(i+1))
        
        return np.asarray(input_v), np.asarray(measured_data)
    
    def _sample_channel(self, channel):
        # print(f'Sampling channel {channel}')
        self.scope.write('header 0')
        self.scope.write('data:encdg SRIBINARY')
        self.scope.write(f'data:source CH{channel}') # channel
        self.scope.write('data:start 1') # first sample
        record = int(self.scope.query('horizontal:recordlength?'))
        self.scope.write('data:stop {}'.format(record)) # last sample
        self.scope.write('wfmoutpre:byt_n 1') # 1 byte per sample

        # # acq config
        # self.scope.write('acquire:state 0') # stop
        # self.scope.write('acquire:stopafter SEQUENCE') # single
        # self.scope.write('acquire:state 1') # run
        # t5 = time.perf_counter()
        # r = self.scope.query('*opc?') # sync
        # t6 = time.perf_counter()
        # print('acquire time: {} s'.format(t6 - t5))

        # data query
        t7 = time.perf_counter()
        bin_wave = self.scope.query_binary_values('curve?', datatype='b', container=np.array)
        t8 = time.perf_counter()
        # print('transfer time: {} s'.format(t8 - t7))

        # retrieve scaling factors
        vscale = float(self.scope.query('wfmoutpre:ymult?')) # volts / level
        voff = float(self.scope.query('wfmoutpre:yzero?')) # reference voltage
        vpos = float(self.scope.query('wfmoutpre:yoff?')) # reference position (level)

        # error checking
        r = int(self.scope.query('*esr?'))
        # print('event status register: 0b{:08b}'.format(r))
        r = self.scope.query('allev?').strip()
        # print('all event messages: {}'.format(r))

        unscaled_wave = np.array(bin_wave, dtype='double') # data type conversion
        scaled_wave = (unscaled_wave - vpos) * vscale + voff
        
        return scaled_wave