"""
Created Feb 7, 2018 by Robert Polski
"""

import numpy as np
from typing import Union

from qcodes import VisaInstrument
from qcodes.instrument.parameter import ArrayParameter, MultiParameter
import qcodes.utils.validators as vals
import time


class Agilent_XGS600(VisaInstrument):
    """The Agilent XGS-600 pressure gauge driver"""
    def __init__(self, name, address):
        super().__init__(name, address, terminator='\r', **kwargs)

        self.add_parameter('pressure_units', get_cmd='#0013')
