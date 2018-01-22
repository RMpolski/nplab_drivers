#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 13:32:00 2018

@author: robertpolski
"""

import numpy as np
from typing import List, Dict, Union, Optional
from functools import partial

import qcodes as qc
from qcodes import VisaInstrument
import qcodes.utils.validators as vals

def parse_output_bool(value):
    if int(value) == 1:
        return True
    elif int(value) == 0:
        return False
    elif value == True or value == False:
        return value
    else:
        raise ValueError('Must be boolean, 0 or 1, True or False')

def parse_input_bool(value):
    if value:
        return True
    else:
        return False

class Keithley_6221(VisaInstrument):
    """
    Instrument Driver for Keithley 6221 current source
    """

    def __init__(self, name: str, address: str, reset: bool=False, **kwargs) -> None:
        """
        Args:
            name: Name to use internally in QCoDeS
            address: VISA ressource address
            reset: Set Keithley to defaults? True or False
        """
        super().__init__(name, address, terminator='\n', **kwargs)

        self.add_parameter('current',
                           get_cmd='SOUR:CURR?',
                           set_cmd='SOUR:CURR {}',
                           get_parser=float,
                           vals=vals.Numbers())

        self.add_parameter('output',
                           get_cmd='OUTP:STAT?',
                           set_cmd='OUTP:STAT {}',
                           get_parser=int,
                           vals=vals.Ints(0,1))
        self.add_parameter('delay',
                           get_cmd='SOUR:DEL?',
                           set_cmd='SOUR:DEL {}',
                           get_parser=float,
                           vals=vals.Numbers(0.001, 999999.999))
        self.add_parameter('display',
                           get_cmd='DISP:ENAB',
                           set_cmd='DISP:ENAB {}',
                           get_parser=int,
                           vals=vals.Ints(0,1))
        self.add_parameter('beeper',
                           get_cmd='SYST:BEEP?',
                           set_cmd='SYST:BEEP {}',
                           get_parser=int,
                           vals=vals.Ints(0,1))


        self.add_function('reset', call_cmd='*RST')

        if reset:
            self.reset()

        self.connect_message()