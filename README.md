# nplab_drivers
Some drivers in development for the Nadj-Perge Group at Caltech.
To be used along with the QCoDes environment, which you can clone:
https://github.com/QCoDeS/Qcodes.git

Clone this repository into the instrument_drivers folder where QCoDeS is installed in your working python distribution. Ex: <path_to>/anaconda/envs/qcodes/lib/python3.6/site-packages/qcodes/qcodes/instrument_drivers

You also will need, for the Dynacool PPMS system, to use the command "conda install pywin32" while in the qcodes environment to have the right packages for the driver QD.py.

The intent is to make a Keithley 6221-2182a combined instrument (and possibly experiment with separating the instruments for a QCoDeS-driven sweep) for doing low-noise, low-voltage delta voltage and differential resistance sweeps. The Dynacool PPMS driver "QD.py" works now too. The other instrument that works right now is the OpenDACs DAC_ADC (based on http://opendacs.com/), and the driver for the Seekat (on Arduino Uno) is coming soon. The OpenDACs drivers also require "conda install pyserial", since they use a serial connection to Arduinos.

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

Make sure you're using the qcodes environment when you're opening ipython, spyder, or jupyter sessions.

Import our drivers using, e.g. "from qcodes.instrument_drivers.nplab_drivers.Keithley_6221 import Keithley_6221"
Then instantiate the driver using, e.g. k6 = Keithley_6221('k6', 'GPIB::12::INSTR')
