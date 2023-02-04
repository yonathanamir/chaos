# -*- coding: utf-8 -*-
"""
Created on Sun Nov 20 17:39:19 2022
DataFetchers for RLD circuit data. Includes a base class with test funcationality for debugging purposes and a proper
VisaDevice written to use for Tektronix MDO3000 Series Oscilloscopes

@author: Yonathan
"""

import numpy as np

from visa_device import VisaDevice


class DataFetcher:
    def __init__(self):
        self._data = None
    
    def get_data(self):
        if self._data is None:
            file = r"C:\Users\owner\Desktop\yonathan\week 3\parallel.csv"
            cols = [4, 10]
            
            from chaos import read_data
            cols_data = read_data(file, col=cols)
            input_v = cols_data[0]
            measured_data = cols_data[1:]
            self._data = (np.asarray(input_v), np.asarray(measured_data))
        
        return self._data


class ScopeDataFetcher(VisaDevice):
    def __init__(self, visa_address, channels_to_sample):
        super().__init__(visa_address=visa_address)
        self.scope = self.device
        self.channels_to_sample = channels_to_sample

    def __del__(self):
        self.scope.close()
        self.rm.close()

    # First channel is always treated as input
    # TODO: Generalize this
    @VisaDevice.reconnect_method
    def get_data(self):
        input_v = self._sample_channel(1)
        measured_data = []
        for i in range(1, self.channels_to_sample, 1):
            sampled = self._sample_channel(i+1)
            measured_data.append(sampled)
        
        return np.asarray(input_v), np.asarray(measured_data)
    
    @VisaDevice.reconnect_method
    def _sample_channel(self, channel):
        self.scope.write('header 0')
        self.scope.write('data:encdg SRIBINARY')
        self.scope.write(f'data:source CH{channel}') # channel
        self.scope.write('data:start 1') # first sample
        record = int(self.scope.query('horizontal:recordlength?'))
        self.scope.write('data:stop {}'.format(record)) # last sample
        self.scope.write('wfmoutpre:byt_n 1') # 1 byte per sample

        # data query
        bin_wave = self.scope.query_binary_values('curve?', datatype='b', container=np.array)
        unscaled_wave = np.array(bin_wave, dtype='double')  # data type conversion

        # retrieve scaling factors
        vscale = float(self.scope.query('wfmoutpre:ymult?')) # volts / level
        voff = float(self.scope.query('wfmoutpre:yzero?')) # reference voltage
        vpos = float(self.scope.query('wfmoutpre:yoff?')) # reference position (level)

        scaled_wave = (unscaled_wave - vpos) * vscale + voff
        
        return scaled_wave
