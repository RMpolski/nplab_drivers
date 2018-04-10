# Common Preamble for nplab drivers

import numpy as np
import matplotlib.pyplot as plt
import qcodes as qc
import os


## Change directory to our base directory (or another, if you want)
os.chdir('C:/Users/TFRLab/Documents/Data/Users/NPLab/qcodes_data')

## Uncomment instruments that you need
# from qcodes.instrument_drivers.tektronix.Keithley_2000 import Keithley_2000
# from qcodes.instrument_drivers.nplab_drivers.Keithley_6221 import Keithley_6221
# from qcodes.instrument_drivers.nplab_drivers.Keithley_2182a import Keithley_2182a
# from qcodes.instrument_drivers.nplab_drivers.Keithley_2200 import Keithley_2200
# from qcodes.instrument_drivers.nplab_drivers.QD import QD
# from qcodes.instrument_drivers.nplab_drivers.LR_700 import LR_700
# from qcodes.instrument_drivers.nplab_drivers.OpenDacs_Seekat import Seekat
# from qcodes.instrument_drivers.nplab_drivers.OpenDacs_DAC_ADC import DAC_ADC
from qcodes.instrument_drivers.nplab_drivers.plot_tools import (get2d_dat,
                                                    dvdi2dfromiv, concat_2d,
                                                    val_to_index)
from qcodes.instrument_drivers.nplab_drivers.time_params import (
        time_from_start,
        time_stamp,
        output_datetime,
        output_date_strings)
from qcodes.instrument_drivers.nplab_drivers.common_commands import (
        single_param_sweep,
        twod_param_sweep,
        data_log)


# Uncomment the instruments you need
# k2182 = Keithley_2182a('k2182', 'GPIB::7::INSTR')
# k6 = Keithley_6221('k6', 'GPIB::12::INSTR')
# k2015 = Keithley_2000('k2015', 'GPIB::1::INSTR')
# k2200 = Keithley_2200('k2200', 'GPIB::19::INSTR')
# ppms = QD('ppms')
# seekat = Seekat('seekat', 'COM5', timeout=8)
# dacadc = DAC_ADC('dacadc', 'COM?', timeout=8)
# lr700 = LR_700('lr700', 'GPIB::18::INSTR')
