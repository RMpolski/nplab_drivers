#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 16:38:38 2018
DAC_ADC driver for QCodes, modeled after the do_DAC_ADC driver for qtlab
@author: robertpolski
"""


import numpy as np
import qcodes as qc
from qcodes import Instrument
import qcodes.utils.validators as vals
from qcodes.utils.helpers import strip_attrs
from functools import partial
import serial
import time

# Helper functions ##########################


def ch_convert(ch):
    """ Convert the given channels to the Arduino's internal channels"""

    # Dict has values in a list for: n1, n2, m1, m2
    ch_dict = {1: [19, 0, 1, 0],
               2: [18, 0, 1, 0],
               3: [17, 0, 1, 0],
               4: [16, 0, 1, 0],
               5: [0, 19, 0, 1],
               6: [0, 18, 0, 1],
               7: [0, 17, 0, 1],
               8: [0, 16, 0, 1]}
    if ch not in ch_dict.keys():
        print('Invalid Seekat channel. Must be 1-8')
    ch_list = ch_dict[ch]
    return ch_list


def set_volt(ser, ch, volt):
    ch_list = ch_convert(ch)

    # Convert voltage to its representation
    if volt >= 0:
        dec16 = round((2**15-1)*volt/10)
    else:
        dec16 = round(2**16 - abs(volt)/10.0 * 2**15)

    # Remove case where -0 is used
    if int(dec16) == 2**16:
        dec16 = 0

    # time.sleep(1)  # do we need these?
    bin16 = str(bin(int(dec16))[2:]).zfill(16)  # 16 bit binary
    d1 = int(bin16[:8], 2)  # first 8 bits
    d2 = int(bin16[8:17], 2)  # second 8 bits
    time.sleep(0.005)  # do we need these?

    ser.write([255, 254, 253, ch_list[0], d1*ch_list[2],
              d2*ch_list[2], ch_list[1], d1*ch_list[3],
              d2*ch_list[3]])
    ser.flush()


def get_volt(ser, ch):
    ch_list = ch_convert(ch)

    ser.reset_input_buffer()
    # Add to ch_list
    if ch_list[0]:
        ch_list[0] += 128
    if ch_list[1]:
        ch_list[1] += 128

    time.sleep(0.02)  # do we need these? Couldn't it be 0.02?
    ser.write([255, 254, 253, ch_list[0], 0, 0, ch_list[1], 0, 0])
    time.sleep(0.02)
    ser.write([255, 254, 253, ch_list[0], 0, 0, ch_list[1], 0, 0])
    time.sleep(0.02)
    ser.flush()
    time.sleep(0.02)
    ser.write([255, 254, 253, 0, 0, 0, 0, 0, 0])
    time.sleep(.01)  # and this should be able to be 0.01

    bdata = np.zeros(13)
    for i in range(0, 12):
        bdata[i] = ser.readline()

    bdata2 = max(bdata[7]*2**8 + bdata[8], bdata[10]*2**8 + bdata[11])
    if bdata2 < 2**15:
        bdata3 = 10*bdata2/(2**15-1)
    else:
        bdata3 = -10*(2**16 - bdata2)/2**15

    ser.reset_input_buffer()
    return bdata3


class Seekat(Instrument):
    """
    The OpenDac Seekat DAC instrument. Initialize with
    address: the address of the Arduino Uno ('COM5', for example).
    reset=True sets all DAC voltages to 0.
    The parameters are called by name.ch#, where # is the channel (1-8)
    """
    def __init__(self, name, address, timeout=None, reset=False, **kwargs):
        """
        Args:
            name: Name to use internally in QCoDeS
            address: VISA resource address
            reset: Set all DAC values to 0? True or False
        """
        super().__init__(name, **kwargs)

        self.address = address
        self._open_serial_connection(timeout)

        # Set up parameters to be called by ch#, where # is the channel (1-8)
        for i in range(1, 9):
            self.add_parameter('ch'+str(i), set_cmd=partial(self.DAC_set, i),
                               get_cmd=partial(self.DAC_get, i),
                               unit='V', vals=vals.Numbers(-10, 10))

        if reset:
            self.reset()

    def _open_serial_connection(self, timeout=None):
            ser = serial.Serial(self.address, 9600, timeout=timeout)
            print(ser.isOpen())
            if not (ser.isOpen()):
                ser.open()
            self._ser = ser
            print('Connected to ', self.address)
            # print(self.get_idn())  # for some reason get_idn() doesn't work
            # as the first command, but it works after using other commands.
            # It doesn't work even after waiting like 2 seconds

    def close(self):
        """Irreversibly stop this instrument and free its resources.
        Closes the serial connection too"""
        if hasattr(self, 'connection') and hasattr(self.connection, 'close'):
            self.connection.close()
        ser = self._ser
        ser.close()

        strip_attrs(self, whitelist=['name'])
        self.remove_instance(self)

    def reset(self):
        for i in range(1, 9):
            self.DAC_set(i, 0)

    def DAC_set(self, ch, volt):
        set_volt(self._ser, ch, volt)

    def DAC_get(self, ch):
        return get_volt(self._ser, ch)
