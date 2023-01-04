# -*- coding: utf-8 -*-
"""
Created on Wed Dec 28 16:43:01 2022

@author: LAB2_211054
"""

import time # std module
import pyvisa as visa # http://github.com/hgrecco/pyvisa

visa_address = 'USB0::0x0699::0x0346::C037087::INSTR'

rm = visa.ResourceManager()
pws = rm.open_resource(visa_address)
pws.timeout = 10000 # ms
pws.encoding = 'latin_1'
pws.read_termination = '\n'
pws.write_termination = None
pws.write('*cls') # clear ESR

print(pws.query('*idn?'))
# pws.write(f'OUTP ON')
for v in range(0, 10):
    pws.write(f'VOLT {v}')
    time.sleep(0.01)
    
for f in range(0, 50000):
    pws.write(f'FREQ {f}')

print('done')