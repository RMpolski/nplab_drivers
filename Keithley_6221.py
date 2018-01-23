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
from qcodes.instrument.parameter import ArrayParameter
import qcodes.utils.validators as vals

def parse_output_bool(value):
    if int(value) == 1 or int(value) == 0:
        return int(value)
    elif value == True or value == False:
        return int(value)
    elif value == 'on' or value == 'ON':
        return 1
    elif value == 'off' or value == 'OFF':
        return 0
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
                           label='Current (A)',
                           get_cmd='SOUR:CURR?',
                           set_cmd='SOUR:CURR {}',
                           get_parser=float,
                           unit='A',
                           vals=vals.Numbers())
        self.add_parameter('output',
                           get_cmd='OUTP:STAT?',
                           set_cmd='OUTP:STAT {}',
                           get_parser=int,
                           set_parser=parse_output_bool,
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
                           set_parser=parse_output_bool,
                           vals=vals.Ints(0,1))
        self.add_parameter('beeper',
                           get_cmd='SYST:BEEP?',
                           set_cmd='SYST:BEEP {}',
                           get_parser=int,
                           set_parser=parse_output_bool,
                           vals=vals.Ints(0,1))

        # Related to attached 2182(a) nanovoltmeter
        self.add_parameter('unit',
                           get_cmd='UNIT?',
                           set_cmd='UNIT {}',
                           vals=vals.Enum('V', 'ohms', 'OHMS', 'S', 'SIEM',
                                          'siem', 'siemens', 'SIEMENS'))
        self.add_parameter('k2182_present',
                           get_cmd='SOUR:DELT:NVPR?',
                           get_parser=int)
        self.add_parameter('delta_arm',
                           get_cmd='SOUR:DELT:ARM?',
                           get_parser=int)
        self.add_parameter('diff_arm',
                           get_cmd='SOUR:DCON:ARM?',
                           get_parser=int)
        #The following are only settable for now
        self.add_parameter('k2_range',
                           set_cmd='SYST:COMM:SER:SEND "VOLT:RANG {}"',
                           vals=vals.Numbers(0,120))
        self.add_parameter('k2_nplc',
                           set_cmd='SYST:COMM:SER:SEND "VOLT:NPLC {}"',
                           vals=vals.Numbers(0.01,60))
        self.add_parameter('k2_line_sync',
                           set_cmd='SYST:COMM:SER:SEND "SYST:LSYN {}"',
                           set_parser=int,
                           vals=vals.Ints(0,1))
        self.add_parameter('k2_front_autozero',
                           set_cmd='SYST:COMM:SER:SEND "SYST:FAZ {}"',
                           set_parser=int,
                           vals=vals.Ints(0,1))
        self.add_parameter('k2_autozero',
                           set_cmd='SYST:COMM:SER:SEND "SYST:AZER {}"',
                           set_parser=int,
                           vals=vals.Ints(0,1))


        self.add_function('abort_arm', call_cmd='SOUR:SWE:ABOR')
        self.add_function('reset', call_cmd='*RST')
        self.add_function('get_error', call_cmd='SYST:ERR?')

        if reset:
            self.reset()

        self.connect_message()

    def delta_trigger_return(self):
        """ Triggers, waits, parses, and returns the results of a delta sweep.

        The array is of shape (points, 2), where the first column is the
        time between the initial data point and the given data point, and
        the second column is the value"""
        if self.delta_arm() != 1 or self.diff_arm() != 1:
            print('Need to run a delta or differential conductance setup')
            return

        self.write('INIT:IMM')

        qc.Wait(self._delta_delay*self._delta_points)
        # reset the timeout to account for possible extra time
        self._old_timeout = self.timeout()
        if self._delta_points/2 > 5:
            self.timeout(self._delta_points/2)
        else:
            self.timeout(5)
        count = 0
        while not int(self.ask('*OPC?')):# Wait until done. Try if this works...
            qc.Wait(1)
            if count > 5:
                print('Delta function did not appear to finish')
                break
            count += 1

        self.timeout(self._old_timeout)

        _floatdata= np.fromstring(self.ask('TRAC:DATA'), sep=',')
        _vals = np.zeros(int(len(_floatdata)/2))

        if self._delta_time_meas:
            _times = np.zeros(int(len(_floatdata)/2))
            for i in range(len(_floatdata)):
                if np.mod(i, 2) == 0:
                    _vals[int(i/2)] = _floatdata[i]
                else:
                    _times[int((i-1)/2)] = _floatdata[i]
            return np.column_stack((_times, _vals))
        else:
            for i in range(len(_floatdata)):
                if np.mod(i, 2) == 0:
                    _vals[int(i/2)] = _floatdata[i]
            return _vals


    def const_delta_setup(self, high: Union[int, float], points: int, delay=0,
                        low: Union[int, float, None]=None, cab: bool=False,
                        timemeas: bool=False) -> None:
        """ Sets up (doesn't run yet) the 6221 and 2182(a) into Delta mode
        in which the 6221 current source starts with a current at high (Amps)
        then to low (A) and back, and so on for "points" number of data
        points. If no low is given, it's set to the negative of high. Delay
        is the amount of time (in seconds) to wait before measuring after
        flipping from high to low or vice versa. The argument cab is whether
        or not to abort when compliance is entered.

        The function checks if the 2182 is connected over the RS-232 port
        and leaves the 6221 in an armed state.

        Lastly, the function creates a gettable array parameter for the setup
        called constdelta, with setpoints as the mean current. The timemeas
        argument determines whether or not the parameter will include time
        in one column or not.
        Note: you have to run the abort_arm() function after you're done
        running sweeps to unarm."""

        if self.delta_arm() == 1:
            print('Delta mode is already armed. Need to abort or run.')
            return
        elif self.diff_arm() == 1:
            print('Differential conductance is armed. Need to abort first.')
            return

        if self.k2182_present() != 1:
            print('2182 is not connected properly through the RS-232 port')
            return

        self.write('SOUR:DELT:HIGH {}'.format(high))

        if low != None:
            self.write('SOUR:DELT:LOW {}'.format(low))
        else:
            low = -high

        if cab:
            self.write('SOUR:DELT:CAB 1')
        else:
            self.write('SOUR:DELT:CAB 0')

        self.write('SOUR:DELT:DEL {}'.format(delay))
        self.write('SOUR:DELT:COUN {}'.format(points))
        self.write('TRAC:POIN {}'.format(points))
        self.write('SOUR:DELT:ARM')

        self.sweep_current = np.ones(points)*(high-low)/2
        self._delta_delay = delay
        self._delta_points = points

        if 'constdelta' in self.parameters:
            del self.parameters['constdelta']

        if timemeas:
            self.add_parameter('constdelta', parameter_class=ArrayParameter,
                               shape=(points, 2),
                               setpoints=(tuple(self.sweep_current)),
                               setpoint_labels=('Current (A)'),
                               get_cmd=self.delta_trigger_return)
            self._delta_time_meas = True
        else:
            self.add_parameter('constdelta', parameter_class=ArrayParameter,
                               shape=(points,),
                               setpoints=(tuple(self.sweep_current)),
                               setpoint_labels=('Current (A)'),
                               get_cmd=self.delta_trigger_return)
            self._delta_time_meas = False

    def delta_diff_setup(self, start: Union[int, float], stop: Union[int, float],
                         step: Union[int, float], delta: Union[int, float]=1e-6,
                         delay=0, cab: bool=False, timemeas: bool=False) -> None:
        """ Sets up (doesn't run yet) the 6221 and 2182(a) into Delta
        differential conductance mode. The unit can be configured with .unit().
        The 6221 current source alternates and sweeps from start to end, with
        step between the two.

        delta: amount the delta mode jumps above and below the step value
        delay: amount of time (in seconds) to wait before measuring after
        changing sweep values.
        cab: whether or not to abort when compliance is entered.

        The function checks if the 2182 is connected over the RS-232 port
        and leaves the 6221 in an armed state.

        Lastly, the function creates a gettable array parameter for the setup
        called constdelta, with setpoints as the mean current. The timemeas
        argument determines whether or not the parameter will include time
        in one column or not.
        Note: you have to run the abort_arm() function after you're done
        running sweeps to unarm."""

        if self.delta_arm() == 1:
            print('Delta mode is armed. Need to abort first.')
            return
        elif self.diff_arm() == 1:
            print('Differential conductance mode is already armed. Abort or run.')
            return

        if self.k2182_present() != 1:
            print('2182 is not connected properly through the RS-232 port')
            return

        self.write('SOUR:DCON:START {}'.format(start))
        self.write('SOUR:DCON:STOP {}'.format(stop))
        self.write('SOUR:DCON:STEP {}'.format(step))
        self.write('SOUR:DCON:DELTA {}'.format(delta))
        self.write('SOUR:DCOND:DEL {}'.format(delay))

        if cab:
            self.write('SOUR:DCON:CAB 1')
        else:
            self.write('SOUR:DCON: CAB 0')

        #calculate number of points
        self._delta_points = int(np.abs((stop-start)/step)) #provide a checker for if step is right
        self.write('TRAC:POIN {}'.format(self._delta_points))

        self.write('SOUR:DCOND:ARM')

        self.sweep_current = np.arange(start, stop, step)
        self._delta_delay = delay

        if 'deltadcon' in self.parameters:
            del self.parameters['deltadcon']

        if timemeas:
            self.add_parameter('deltadcon', parameter_class=ArrayParameter,
                               shape=(self._delta_points, 2),
                               setpoints=(tuple(self.sweep_current)),
                               setpoint_labels=('Current (A)'),
                               get_cmd=self.delta_trigger_return)
            self._delta_time_meas = True
        else:
            self.add_parameter('deltadcon', parameter_class=ArrayParameter,
                               shape=(self._delta_points,),
                               setpoints=(tuple(self.sweep_current)),
                               setpoint_labels=('Current (A)'),
                               get_cmd=self.delta_trigger_return)
            self._delta_time_meas = False