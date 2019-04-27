#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Friday April 26, 2019

@author: robertpolski
"""

import numpy as np
from typing import Union

from qcodes import VisaInstrument
from qcodes.instrument.parameter import ArrayParameter, MultiParameter
import qcodes.utils.validators as vals
import time
from functools import partial


def parse_bool(value):
    if type(value) is float:
        value = int(value)
    elif type(value) is str:
        value = value.lower()

    if value in {1, 'on', True}:
        return 1
    elif value in {0, 'off', False}:
        return 0
    else:
        print(value)
        raise ValueError('Must be boolean, on or off, 0 or 1, True or False')


# def parse_inp_bool(value):
#     if type(value) is float:
#         value = int(value)
#     elif type(value) is str:
#         value = value.lower()
#
#     if value in {1, 'on', True}:
#         return 'ON'
#     elif value in {0, 'off', False}:
#         return 'OFF'
#     else:
#         print(value)
#         raise ValueError('Must be boolean, on or off, 0 or 1, True or False')


boolcheck = (0, 1, 'on', 'off', 'ON', 'OFF', False, True)


class SIM900(VisaInstrument):
    """
    Instrument Driver for the SRS Frame SIM900. Configure this class if you
    change the instruments and their port orders in the rack. Note that you
    must reset or write the escape string if you connect to any single port
    (using "CONN p,'escapestring'")
    """
    def __init__(self, name: str, address: str, reset: bool=False, **kwargs):
        """
        Args:
            name: Name to use internally in QCoDeS
            address: VISA ressource address
            reset: Reset SIM900, reset voltage sources (set to zero and output
               off)
        """
        super().__init__(name, address, terminator='\n', **kwargs)

        self.add_parameter('volt_p1', label='Port 1 Voltage', unit='V',
                           set_cmd=partial(self.setvolt, 1, 'VOLT'),
                           get_cmd=partial(self.get_from_port, 1, 'VOLT?'),
                           get_parser=float,
                           vals=vals.Numbers(-20, 20))

        self.add_parameter('volt_p5', label='Port 5 Voltage', unit='V',
                           set_cmd=partial(self.setvolt, 5, 'VOLT'),
                           get_cmd=partial(self.get_from_port, 5, 'VOLT?'),
                           get_parser=float,
                           vals=vals.Numbers(-20, 20))

        self.add_parameter('output_p1',
                           set_cmd=partial(self.write_to_port, 1, 'EXON'),
                           get_cmd=partial(self.get_from_port, 1, 'EXON'),
                           set_parser=parse_bool,
                           get_parser=parse_bool,
                           vals=vals.Enum(*boolcheck))

        self.add_parameter('output_p5',
                           set_cmd=partial(self.write_to_port, 5, 'EXON'),
                           get_cmd=partial(self.get_from_port, 5, 'EXON'),
                           set_parser=parse_bool,
                           get_parser=parse_bool,
                           vals=vals.Enum(*boolcheck))

        self.write_to_port(1, 'TERM', 2)
        self.write_to_port(1, 'TERM', 2)
        if reset:
            self.reset()

        self.connect_message()

    def connect_message(self, **kwargs):
        super().connect_message(idn_param='*IDN', **kwargs)

    def reset(self):
        self.write_to_port(1, '*RST', '')
        self.write_to_port(5, '*RST', '')
        self.write('*RST')

    def write_to_port(self, port, message, val):
        sendmess = message + ' {}'.format(val)
        s = 'SNDT {},'.format(int(port) + '"{}"'.format(sendmess))
        self.write(s)
        time.sleep(0.05)

    def get_from_port(self, port, message):
        s = 'SNDT {},'.format(int(port)) + '"{}"'.format(message)
        ans = self.ask(s)
        time.sleep(0.05)
        return ans

    def setvolt(self, port, message, val):
        self.write_to_port(port, message, np.round(val, 3))
