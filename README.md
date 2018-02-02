## nplab_drivers
Some drivers in development for the Nadj-Perge Group at Caltech.
To be used along with the QCoDes environment, which you can clone:
https://github.com/QCoDeS/Qcodes.git

Clone this repository into the instrument_drivers folder where QCoDeS is installed in your working python distribution. Ex: <path_to>/anaconda/envs/qcodes/lib/python3.6/site-packages/qcodes/qcodes/instrument_drivers

You also will need, for the Dynacool PPMS system, to use the command "conda install pywin32" while in the qcodes environment to have the right packages for the driver QD.py.

The intent is to make a Keithley 6221-2182a combined instrument (and possibly experiment with separating the instruments for a QCoDeS-driven sweep) for doing low-noise, low-voltage delta voltage and differential resistance sweeps. The Dynacool PPMS driver "QD.py" works now too. The other instrument that works right now is the OpenDACs DAC_ADC (based on http://opendacs.com/), and the driver for the Seekat (on Arduino Uno) is coming soon. The OpenDACs drivers also require "conda install pyserial", since they use a serial connection to Arduinos.

# Directions for setup:
Download the environment.yml file from the QCodes page and use "conda env create -f path-to-environment.yml" to set up the environment called "qcodes".

Switch to this environment with "activate qcodes" (or "source activate qcodes" on Mac/Linux)

Install git and use "git clone https://github.com/QCoDeS/Qcodes.git" in the desired location (I use some variant of Anaconda/envs/qcodes/Lib/site-packages as the directory). Change the directory name to qcodes.

Install the qcodes package with "pip install -e path-to-qcodes-directory".

Clone the nplab_drivers github repository into "path-to/qcodes/qcodes/instrument_drivers"
"git clone https://github.com/RMpolski/nplab_drivers.git"

Also install other packages into the qcodes environment.
"conda install pywin32" for the PPMS driver
"conda install pyserial" for the OpenDACs drivers

Use git pull while in the nplab_drivers directory to get the latest updates.

Make sure you're using the qcodes environment, and enjoy!
