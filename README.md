# nplab_drivers
Some drivers in development for the Nadj-Perge Group at Caltech.
To be used along with the QCoDes environment, which you can clone:
https://github.com/QCoDeS/Qcodes.git

Clone this repository into the instrument_drivers folder where QCoDeS is installed in your working python distribution. Ex: <path_to>/anaconda/envs/qcodes/lib/python3.6/site-packages/qcodes/qcodes/instrument_drivers

You also will need, for the Dynacool PPMS system, to use the command "conda install pywin32" while in the qcodes environment to have the right packages for the driver QD.py.

The current working drivers are:
Keithley_6221 (except for the delta_IV_sweep_get command and displaying error messages)
Keithley_2182a
QD (for a Quantum Design Dynacool PPMS system)
DAC_AC (from openDacs http://opendacs.com/)
Seekat (also from openDacs)

Also a little package with simple commands in case anyone wants to be more time-conscious with the experiments. It has gettable time parameters that output floats and methods of changing these floats into date/time strings or python datetime objects (accurate to milliseconds):
time_params

Note: QD requires "conda install pywin32" since it connects through the MultiVu program on windows (and therefore would need some help to work on a Mac), and the OpenDACs drivers require "conda install pyserial", since they use a serial connection to Arduinos (but they also work on Macs). Find the GPIB addresses for the Keithleys in the NI MAX software, and find the Arduino addresses through the Arduino program (on Mac it will look like /dev/cu.*******, and on Windows a mores simple 'COM3' or with some other number). QD only requires the MultiVu software and no address.

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
