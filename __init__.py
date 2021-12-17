import sys
import subprocess

from ..tektronix.Keithley_2000 import Keithley_2000
from .Keithley_6221 import Keithley_6221
from .Keithley_2182a import Keithley_2182a
from .Keithley_2200 import Keithley_2200
from .LR_700 import LR_700
from .SIM900 import SIM900
from .SIM900_stick import SIM900_stick
from .SIM900_rs232 import SIM900_rs232
from .OpenDacs_Seekat import Seekat
from .OpenDacs_DAC_ADC import DAC_ADC
from ..stanford_research.SR830 import SR830
from ..stanford_research.SR865A import SR865A
from .vdpArduino import vdpArduino
from .NPTriton import Triton
from .SR560 import SR560
from .SRDC205 import SRDC205
from .Lakeshore211 import Lakeshore211
from .plot_tools import (get2d_dat,
                        dvdi2dfromiv, concat_2d,
                        val_to_index, mov_average,
                        iv_from_dvdi,
                        Rxxfromdata,
                        RapidTwoSlopeNorm,
                        DivLogNorm,
                        DivSymLogNorm,
                        graphene_mobilityFE,
                        graphene_mobilityB,
                        gr_Boltzmannfit)

from .time_params import (
        time_from_start,
        time_stamp,
        output_datetime,
        output_date_strings)

from .common_commands import (
        single_param_sweep,
        twod_param_sweep,
        data_log, breakat)


from .instrumentinitialize import (
        ppms_init,
        triton_init,
        stick_setup_init)

from .bipolarcolor import bipolar

if sys.platform == 'win32':
    from .QD import QD

reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
installed_packages = [r.decode() for r in reqs.split()]
if 'qtplot==0.2.5' in installed_packages:
    from .plot_tools import qt2dplot
