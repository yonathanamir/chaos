# -*- coding: utf-8 -*-
"""
Created on Fri Dec 30 02:02:40 2022

@author: Yonathan
"""

import pyvisa as visa


class VisaDevice:
    def __init__(self, visa_address, timeout=10000, encoding='latin_1',
                 read_termination='\n', write_termination=None):
        self.visa_address = visa_address
        self.rm = visa.ResourceManager()
        self.device = self.rm.open_resource(self.visa_address)
        
        self.device.timeout = timeout # ms
        self.device.encoding = encoding
        self.device.read_termination = read_termination
        self.device.write_termination = write_termination
        
        self.device.write('*cls')  # clear ESR
        
    def __del__(self):
        self.device.close()
        self.rm.close()
        