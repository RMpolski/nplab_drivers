#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 08:11:41 2018

Keithley_2182a attempt from scratch. Mostly derived from the Keithley_2600_channels script
@author: robertpolski
"""


import numpy as np
from typing import List, Dict, Union, Optional
from functools import partial

import qcodes as qc
from qcodes import VisaInstrument
import qcodes.utils.validators as vals

def parse_output_string(s):
    """ Parses and cleans string outputs of the Keithley """
    # Remove surrounding whitespace and newline characters
    s = s.strip()

    # Remove surrounding quotes
    if (s[0] == s[-1]) and s.startswith(("'", '"')):
        s = s[1:-1]

    #s = s.lower() #Try commenting this out. I don't like it much

    # Convert some results to a better readable version
    conversions = {
        'mov': 'moving',
        'rep': 'repeat',
    }

    if s.lower() in conversions.keys(): # To comment out line 28, changed here too
        s = conversions[s]
    
    if s[-3:] == ':DC':
        s = s[:-3]

    return s

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

#%%
class Keithley_2182a(VisaInstrument):
    """
    The Instrument driver for the Keithley 2182a nanovoltmeter
    """
    def __init__(self, name: str, address: str, reset: bool=False, **kwargs) -> None:
        """
        Args:
            name: Name to use internally in QCoDeS
            address: VISA ressource address
            reset: Set Keithley to defaults? True or False
        """
        super().__init__(name, address, terminator='\n', **kwargs)

        # The limits of the range function. There's a separate function for
        # autorange
        self.vranges = [[0.01, 0.1, 1., 10., 100.], [0.1, 1, 10]]
        self.tempranges = []

        self.add_parameter('mode',
                           get_cmd='SENS:FUNC?',
                           set_cmd='SENS:FUNC {}',
                           vals = vals.Enum('VOLT', 'TEMP'))

        self.add_parameter('channel',
                           get_cmd='SENS:CHAN?',
                           set_cmd='SENS:CHAN {}',
                           vals=vals.Ints(0,2))

        self.add_parameter('range',
                           get_cmd=partial(self._get_mode_param_chan, 'RANG',
                                           float),
                           set_cmd=partial(self._set_mode_param_chan, 'RANG'),
                           get_parser=float,
                           vals=vals.Numbers(0, 120)) #connect to _mode_range through enum

        self.add_parameter('auto_range_enabled',
                           get_cmd=partial(self._get_mode_param, 'RANG:AUTO',
                                           parse_output_bool),
                           set_cmd=partial(self._set_mode_param, 'RANG:AUTO'),
                           vals=vals.Bool())

        self.add_parameter('measure',
                           get_cmd='SENS:DATA:FRES?',
                           get_parser=float,
                           vals=vals.Numbers(),
                           unit='V') #change to pull from the measurement type

        self.add_parameter('nplc',
                           get_cmd=partial(self._get_mode_param, 'NPLC',
                                           float),
                           set_cmd=partial(self._set_mode_param, 'NPLC'),
                           get_parser=float,
                           vals=vals.Numbers(0.01,60))

        self.add_parameter('line_sync',
                           get_cmd='SYST:LSYN?',
                           set_cmd='SYST:LSYN {}',
                           vals=vals.Bool(),
                           get_parser=parse_output_bool,
                           set_parser=int)

        self.add_parameter('front_autozero',
                           get_cmd='SYST:FAZ?',
                           set_cmd='SYST:FAZ {}',
                           get_parser=parse_output_bool,
                           set_parser=int,
                           vals=vals.Bool())

        self.add_parameter('autozero',
                           get_cmd='SYST:AZER?',
                           set_cmd='SYST:AZER {}',
                           get_parser=parse_output_bool,
                           set_parser=int,
                           vals=vals.Bool())
        self.add_parameter('temp_unit',
                           get_cmd='UNIT:TEMP?',
                           set_cmd='UNIT:TEMP {}',
                           get_parser=parse_output_string,
                           vals=vals.Enum('C', 'F', 'K'))
        
        self.add_parameter('display',
                           get_cmd='DISP:ENAB',
                           set_cmd='DISP:ENAB {}',
                           get_parser=int,
                           vals=vals.Ints(0,1))
        self.add_parameter('beeper',
                           get_cmd='SYST:BEEP?',
                           set_cmd='SYST:BEEP {}',
                           vals=vals.Ints(0,1))

        self.add_function('reset', call_cmd='*RST')
        self.add_function('last_error', call_cmd='STAT:QUE:NEXT?')


        if reset:
            self.reset()

        self.connect_message()

    def autocalibrate(self):
        """Initializes calibration, asks if you want to continue, and
        does low-level calibration. It's recommended if the
        temperature difference is above 1 deg C.
        Takes about 5 minutes if you continue"""
        self.write('CAL:UNPR:ACAL:INIT')
        prevtemp = parse_output_string(self.ask('CAL:UNPR:ACAL:TEMP?'))
        currtemp = parse_output_string(self.ask('SENS:TEMP:RTEM?'))

        answer = input('The last time ACAL was run,'+
                       'the temp was {} C\n'.format(prevtemp)+
              'Now the temp is {} C\n'.format(currtemp)+
              'Do you want to proceed with low-level calibration? [y/n] ')
        b = answer == 'y' and parse_output_string(self.mode()) == 'volt'
        b = b and float(parse_output_string(self.range())) == 0.01
        if b:
            self.write('CAL:UNPR:ACAL:STEP2')
            self.write('CAL:UNPR:ACAL:DONE')
        elif answer == 'n':
            self.write('CAL:UNPR:ACAL:DONE')
        else:
            print('Must be in voltage mode, range 10mV')
            self.write('CAL:UNPR:ACAL:DONE')


    def _get_mode_param(self, parameter: str, parser):
        """ Read the current Keithley mode and ask for a parameter """
        mode = parse_output_string(self.mode())
        cmd = 'SENS:{}:{}?'.format(mode, parameter)

        return parser(self.ask(cmd))

    def _get_mode_param_chan(self, parameter: str, parser, chan=None):
        """ Read the current Keithley mode and ask for a parameter """
        mode = parse_output_string(self.mode())
        if chan == None:
            chan = parse_output_string(self.channel())
        cstring = 'CHAN{}'.format(chan)
        cmd = 'SENS:{}:{}:{}?'.format(mode, cstring, parameter)

        return parser(self.ask(cmd))

    def _set_mode_param(self, parameter: str, value):
        """ Read the current Keithley mode and set a parameter """
        if isinstance(value, bool):
            value = int(value)

        mode = parse_output_string(self.mode())
        cmd = 'SENS:{}:{} {}'.format(mode, parameter, value)
        self.write(cmd)

    def _set_mode_param_chan(self, parameter: str, value, chan=None):
        """ Read the current Keithley mode and set a parameter """
        if isinstance(value, bool):
            value = int(value)

        mode = parse_output_string(self.mode())
        if chan == None:
            chan = parse_output_string(self.channel())
        cstring = 'CHAN{}'.format(chan)
        cmd = 'SENS:{}:{}:{} {}'.format(mode, cstring, parameter, value)
        self.write(cmd)

    def _mode_range(self):
        """ Returns the different range settings for a given mode """
        if self.channel() == 0:
            raise ValueError('Needs to be set on channel 1 or 2')
        if self.mode() == 'VOLT':
            return self.vranges[self.channel()-1]
        elif self.mode() == 'TEMP':
            return self.tempranges[self.channel()-1]
        else:
            raise ValueError('Not VOLT or TEMP in _mode_range')

    def _digit_range(self):
        """ Feeds number of digit min and max to Enum validator"""
        if self.mode() == 'VOLT':
            return np.arange(3.5, 8, 0.5)
        elif self.mode() == 'TEMP':
            return np.arange(4, 8, 1)
        else:
            raise ValueError('Must be VOLT or TEMP in _digit_range')

    def _get_unit(self):
        """ Returns the unit for the current measurement mode"""
        if self.mode() == 'VOLT':
            return 'V'
        elif self.mode() == 'TEMP':
            return self.ask('UNIT:TEMP?')
        else:
            raise ValueError('Mode must be VOLT or TEMP')
