from qcodes.instrument_drivers.nplab_drivers.plot_tools import (get2d_dat,
                                                    dvdi2dfromiv, concat_2d)


def import_npd(*args):
    if 'k6' in args:
        from qcodes.instrument_drivers.nplab_drivers.Keithley_6221 import Keithley_6221
    if 'k2182' in args:
        from qcodes.instrument_drivers.nplab_drivers.Keithley_2182a import Keithley_2182a
    if 'k2200' in args:
        from qcodes.instrument_drivers.nplab_drivers.Keithley_2200 import Keithley_2200
    if 'qd' in args:
        from qcodes.instrument_drivers.nplab_drivers.QD import QD
    if 'lr' in args:
        from qcodes.instrument_drivers.nplab_drivers.LR_700 import LR_700
    if 'seekat' in args:
        from qcodes.instrument_drivers.nplab_drivers.OpenDacs_Seekat import Seekat
    if 'dac_adc' in args:
        from qcodes.instrument_drivers.nplab_drivers.OpenDacs_DAC_ADC import DAC_ADC
