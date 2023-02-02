# -*- coding: utf-8 -*-
"""
Created on Fri Dec 30 02:02:40 2022
General Visa Device base class.

@author: Yonathan
"""

import time
import pyvisa as visa
PRINT = False
SLEEP_INTERVAL = 1


class VisaDevice:
    def __init__(self, visa_address, timeout=1000, encoding='latin_1',
                 read_termination='\n', write_termination=None):
        self.visa_address = visa_address
        self.rm = visa.ResourceManager()
        self.connect()
        
        self.device.timeout = timeout  # in ms
        self.device.encoding = encoding
        self.device.read_termination = read_termination
        self.device.write_termination = write_termination
        
        self.device.write('*cls')  # clear ESR
        
    def __del__(self):
        self.device.close()
        self.rm.close()

    def connect(self):
        self.device = self.rm.open_resource(self.visa_address)
        self.connected = True
        
    def reconnect_method(func):
        def inner(self, *args, **kwargs): 
            while True:
                try:
                    return func(self, *args, **kwargs)
                except Exception as ex:
                    self.connected = False
                    if PRINT:
                        print(f"Caught Exception {ex}, reconnecting.")

                    while not self.connected:
                        try:
                            time.sleep(SLEEP_INTERVAL)
                            self.connect()
                        except Exception as ex2:
                            if PRINT:
                                print(f"Caught Exception {ex2} while reconnection, trying again.")

        return inner