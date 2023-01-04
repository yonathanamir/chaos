# -*- coding: utf-8 -*-
"""
Created on Fri Dec 30 02:10:13 2022

@author: Yonathan
"""

from visa_device import VisaDevice


class AwgDevice(VisaDevice):
    def __init__(self, visa_address):
        super().__init__(visa_address=visa_address)

        # TODO: AC Base Commands

    @property
    def voltage(self):
        return self.device.query(f'volt?')
    @voltage.setter
    def voltage(self, value):
        self.device.write(f'volt {round(value, 3)}')
    
    
    @property
    def frequency(self):
        return self.device.query('freq?')
    @frequency.setter
    def frequency(self, value):
        self.device.write(f'freq {round(value, 3)}')