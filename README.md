## nplab_drivers
Some drivers in development for the Nadj-Perge Group at Caltech.
To be used along with the QCoDes environment, which you can clone:
https://github.com/QCoDeS/Qcodes.git

Clone this repository into the instrument_drivers folder where QCoDeS is installed in your working python distribution. Ex: <path_to>/anaconda/lib/Python3.6/site-packages/qcodes/qcodes/instrument_drivers

Right now it just consists of an unfinished Tektronix Keithley 2182a instrument driver based on the previously made 2700 driver already in the QCoDeS repository.
The intent is to make a Keithley 6221-2182a combined instrument (and possibly experiment with separating the instruments for a QCoDeS-driven sweep) for doing low-noise, low-voltage delta voltage and differential resistance sweeps.
