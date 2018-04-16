# nplab_drivers
Some drivers in development for the Nadj-Perge Group at Caltech.
To be used along with the QCoDes environment, which you can clone:
https://github.com/QCoDeS/Qcodes.git

Clone this repository into the instrument_drivers folder where QCoDeS is installed in your working python distribution. Ex: <path_to>/anaconda/envs/qcodes/lib/python3.6/site-packages/qcodes/qcodes/instrument_drivers

Note for using drivers: QD requires "conda install pywin32" since it connects through the MultiVu program on windows (and therefore would need some help to work on a Mac), and the OpenDACs drivers require "conda install pyserial", since they use a serial connection to Arduinos (but they also work on Macs). Find the GPIB addresses for the Keithleys in the NI MAX software, and find the Arduino addresses through the Arduino program (on Mac it will look like /dev/cu.*******, and on Windows a mores simple 'COM3' or with some other number). QD only requires the MultiVu software and no address.

The current working drivers are:
Keithley_6221 (except for the delta_IV_sweep_get command and displaying error messages)
Keithley_2182a
QD (for a Quantum Design Dynacool PPMS system)
DAC_AC (from openDacs http://opendacs.com/)
Seekat (also from openDacs)
LR_700 (for a Lakeshore AC resistance bridge)


## Preamble, useful functions and parameters
Looking at the file common_preamble.py, there's an example preamble of imports that the NP Group can use to easily initialize its instruments. You can also find the preamble at the bottom of this page It also imports useful functions that do the following:

####Functions from common_commands.py
single_param_sweep: takes the parameter to set, an arbitrary array of values to sweep through (can be equally incremented or not), the delay between setting and measuring, and the parameters to measure. Automatically plots all measured parameters in separate plots vs. the set parameter. Plotting can also be controlled by choosing the x and y parameters to plot. Also, you can choose a name for the dataset.
twod_param_sweep: same, but now there are two set parameters and a set array for each
data_log: For use when you want to measure some parameters over time. Plots the results in the same fashion as above and returns the time since the start as one of the measurements. Choose the delay (this time the delay after measurement) and the measurement parameters. You also need either a total number of measurements to take or the amount of minutes to record measurements (+ extra time added for the time it takes to perform each measurement).

####Imports from time_params.py
time_from_start: a qcodes parameter with a get command that returns the time since its creation or the time since its last .reset()
time_stamp: a qcodes parameter with a get command that returns the standard Python float that represents a time stamp in the datetime package (time in seconds since December 31, 4:00 pm, 1969)
output_datetime: can input a number or array of numbers in the format of Python's timestamp and get an array of Python datetime objects that can be used for plotting or other functions. Also can choose the start date and time if not a standard Python timestamp.
output_date_strings: same but outputs strings that represent the date (the string format can also be modified easily)

####Functions from plot_tools
val_to_index: useful for picking out rows or columns in a 2D dataset to plot multiple 1D lines. Input the array of values to find and the array to look in, and it will return an array of where it found those values (or their nearest estimates)
get_2d_dat: generates X, Y, Z arrays that can be used in matplotlib's pcolormesh from a qcodes .dat saved file
dvdi2dfromiv: generates 2D dV/dI or dI/dV arrays (X, Y, Z as above) from a qcodes dataset where an IV (source current, measure voltage) sweep was done
concat_2d: Adds and sews in 2D qcodes datasets to each other and outputs X, Y, Z arrays as above. Assumes the x-parameter (or inner loop) is the same for each dataset


### Calculated parameters
Also note that you can make a calculated parameter pretty easily. If the value provided by instr.param() needs
to have an operation done to it before you want it displayed in the
measurement, use a parameter defined this way. Define your own function that
returns what you want, using OhmsfromI as an example.
constV = 0.5
def OhmsfromI():
    return constV/instr.current()


paramname = qc.Parameter('paramname', get_cmd=OhmsfromI, label='Resistance',
                         unit='Ohms')


## Directions for setup:
Install Anaconda form https://www.anaconda.com/download/

Download the environment.yml file from the QCodes page (https://raw.githubusercontent.com/QCoDeS/Qcodes/master/environment.yml) and use "conda env create -f path-to-environment.yml" to set up the environment called "qcodes".

If on Windows, you can now open a session in qcodes by opening the anaconda navigator, selecting qcodes from the environments drop-down menu, and selecting ipython, a jupyter notebook, or a spyder session. Or switch to this environment through the anaconda prompt with "activate qcodes" (or "source activate qcodes" on Mac/Linux terminal).

Install git from https://git-scm.com/downloads. Now you can use git in the regular windows command prompt.

Open a windows command prompt, use "cd path-to-directory" to choose the directory where you want to deposit the qcodes package, and enter the command "git clone https://github.com/QCoDeS/Qcodes.git" (I use some variant of Anaconda/envs/qcodes/Lib/site-packages as the directory). Change the newly cloned directory name form "Qcodes" to qcodes.

In an anaconda prompt, use "activate qcodes" to enter the environment.

Install the qcodes package with "pip install -e path-to-qcodes-directory".

Clone the nplab_drivers github repository into "path-to/qcodes/qcodes/instrument_drivers" by entering the command "git clone https://github.com/RMpolski/nplab_drivers.git"

Also install other packages into the qcodes environment (you should still be in the qcodes environment)
"conda install pywin32" for the PPMS driver
"conda install pyserial" for the OpenDACs drivers

Enter the command "git pull" while in the nplab_drivers directory to get the latest updates to our drivers. Using "git pull" while in the top level of the qcodes directory will not affect our drivers.

Make sure you're using the qcodes environment when you're opening ipython, spyder, or jupyter sessions, or when you run a file the imports things from the qcodes package.

While in a python session or document, if you want to use our drivers, import them using, e.g. "from qcodes.instrument_drivers.nplab_drivers.Keithley_6221 import Keithley_6221"
Then instantiate the driver using, e.g. k6 = Keithley_6221('k6', 'GPIB::12::INSTR')




## Common Preamble for nplab drivers
```
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
                                                    val_to_index,
                                                    iv_from_dvdi)
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
```
