# -*- coding: utf-8 -*-
"""
Created on Fri Dec 30 02:10:13 2022
Control a Tektronix AFG3000 Series A/F Generator

@author: Yonathan
"""

from visa_device import VisaDevice
import time


class AwgDevice(VisaDevice):
    def __init__(self, visa_address):
        super().__init__(visa_address=visa_address)
        self.off_ramp()
    
    def connect(self):
        super().connect()
        self.device.write(f"OUTPut1:STATe ON")

    @property
    @VisaDevice.reconnect_method
    def voltage(self):
        return self.device.query(f'volt?')
    @voltage.setter
    @VisaDevice.reconnect_method
    def voltage(self, value):
        self.device.write(f'volt {round(value, 3)}')
        time.sleep(0.001)
    
    
    @property
    @VisaDevice.reconnect_method
    def frequency(self):
        return self.device.query('freq?')
    @frequency.setter
    @VisaDevice.reconnect_method
    def frequency(self, value):
        self.device.write(f'freq {round(value, 3)}')
        time.sleep(0.001)

    def set_ramp(self, am_freq):
        self.device.write(f'sour:am:stat on')
        self.device.write(f'sour:am:dept max')
        self.device.write(f'sour:am:int:freq {am_freq}')
        self.device.write(f'sour:am:int:func ramp')

    def off_ramp(self):
        self.device.write(f'sour:am:stat off')
        