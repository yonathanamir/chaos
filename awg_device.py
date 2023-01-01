# -*- coding: utf-8 -*-
"""
Created on Fri Dec 30 02:10:13 2022

@author: Yonathan
"""

from visa_device import VisaDevice


class AwgDevice(VisaDevice):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

        # TODO: AC Base Commands

    @property
    def voltage(self):
        return self.device.query(f'volt')
    @voltage.setter
    def voltage(self, value):
        self.device.write(f'volt:{round(value, 3)}')
    
    
    @property
    def frequency(self):
        return self.device.query('freqs')
    @frequency.setter
    def frequency(self, value):
        self.device.write(f'freq:{round(value, 3)}')