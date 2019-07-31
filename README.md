# nplab_drivers
Some drivers in development for the Nadj-Perge Group at Caltech.
To be used along with the QCoDes environment, which you can clone (you can clone it to anywhere you want on your computer):
https://github.com/QCoDeS/Qcodes.git

Follow the instructions here to install (based on GitHub, which is more up to date): https://qcodes.github.io/Qcodes/start/index.html

Clone this (nplab_drivers) repository into the instrument_drivers folder where QCoDeS is installed in your working python distribution. Ex: <path_to>/qcodes/qcodes/instrument_drivers

## Note for using drivers:
The instructions here assume you have installed python through anaconda and made an environment called qcodes (as specified in the QCodes installation instructions).

The ppms instrument driver (QD) requires you to install the packages pywin32 (`conda install pywin32`) to the qcodes environment, since the MultiVu program on windows, and the OpenDACs drivers and van-der-Pauw setup require the package pyserial (`conda install pyserial`), since they use a serial connection to Arduinos (but they also work on Macs). Find the GPIB addresses for the Keithleys in the NI MAX software, and find the Arduino addresses through the Arduino program (on Mac it will look like /dev/cu.*******, and on Windows a mores simple 'COM3' or with some other number). QD only requires the MultiVu software and no address.


## Useful functions and parameters

If you want a summary of how to use this (it should also be useful if you've never used QCodes before), open the [NPDrivers_Example_use.ipynb](.NPDrivers_Example_use.ipynb) in a Jupyter Notebook while in the qcodes environment and go through the steps (you can run the code on your computer).

####Functions from common_commands.py
The biggest addition I made was adding 3 commands that summarize most measurements you would need to do in something similar to electrical transport experiments. It uses the what is described in the QCodes documentation as "legacy qcodes" (the database function has since been updated, but mine uses the old version). 

####Instrument initialization
The instrumentinitialize file includes the method I use to quickly initialize the machines that I personally use. You can base your initialization off of this framework, but the details will be specific to your setup. `triton_init()` initializes our dilution fridge and other instruments specified by feeding the string codes of the instruments to the `triton_init()` command. Similarly with `ppms_init()`, which initializes the DynaCool ppms system and other instruments connected to it. This is not a verbose method but based on short names I have for the instruments and keeps consistency on a given instrument. It also prevents me from having to copy GPIB addresses when starting a new experiment.

####Helper commands:
I also added a few functions that I made to help with managing time-based parameters and plotting.


Make sure you're using the qcodes environment when you're opening ipython, spyder, or jupyter sessions, or when you run a file the imports things from the qcodes package.
