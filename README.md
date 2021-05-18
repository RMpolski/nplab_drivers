# nplab_drivers
Some drivers in development for the Nadj-Perge Group at Caltech.
To be used along with the QCoDes setup, which you can clone (you can clone it to anywhere you want on your computer):

`git clone https://github.com/QCoDeS/Qcodes.git`

Instructions on installation: (based on here, with a few changes and clarifications https://qcodes.github.io/Qcodes/start/index.html, although now it's quite a bit different)

First delete the environment.yml folder in the cloned Qcodes repository (top-level folder), and replace it with the environment.yml file in this nplab_drivers repository (download this file separately and do a copy/paste). This allows the live plotting through pyqtgraph to work well by maintaining the old versions of a few packages, and it adds the pyserial package.

(Note, the newest version of qcodes with python 3.8 has some breaking changes, if you still want to use pyqtgraph=0.10.0 and python=3.6.8. I need to test it to see if pyqtgraph works with the new set of packages. Until then, this will only work if you copy over the Qcodes folder from one of our computers.)

Use a prompt to enter the first folder of the cloned Qcodes repository folder. Then make an environment:

`conda env create -f environment.yml`

Enter the qcodes environment:

`conda activate qcodes`

Then install qcodes as a package into this environment from file with

`pip install -e .`

(where the period at the end refers to the current directory).

Clone this (nplab_drivers) repository into the instrument_drivers folder (<path_to>/qcodes/qcodes/instrument_drivers):

```
cd qcodes/instrument_drivers
git clone https://github.com/RMpolski/nplab_drivers.git
```

Then go back and install qcodes again from the top-level folder (this ties up loose ends and allows you to import qcodes.instrument_drivers.nplab_drivers):

```
cd ../..
pip install -e .
```

Lastly, in order to use the plotting style we use, it requires a tweak in the config file. Find the 'Qcodes/qcodes/configuration/qcodesrc.json', or '.../config/qcodesrc.json' file, and change one line. Change it from:

```
"gui" :{
        "notebook": true,
        "plotlib": null,
        "pyqtmaxplots": 100,
        "defaultcolormap": "hot"
    },
 ```
    
 to 
 
 ```
 "gui" :{
        "notebook": true,
        "plotlib": "all",
        "pyqtmaxplots": 100,
        "defaultcolormap": "hot"
    },
 ```
    
 Be careful of the syntax, add the quotation marks, and only change `null` to `"all"`. Now live plotting with pyqtgraph should work well.

## Note for using drivers:
The instructions here assume you have installed python through anaconda and made an environment called qcodes (as specified in the QCodes installation instructions).

The ppms instrument driver (QD) requires you to install the packages pywin32 (`conda install pywin32`) to the qcodes environment, since the MultiVu program on windows. Find the GPIB addresses for the Keithleys in the NI MAX software, and find the Arduino addresses through the Arduino program (on Mac it will look like /dev/cu.*******, and on Windows a mores simple 'COM3' or with some other number). QD only requires the MultiVu software and no address.


## Useful functions and parameters

If you want a summary of how to use this (it should also be useful if you've never used QCodes before), open the [NPDrivers_Example_use.ipynb](NPDrivers_Example_Use.ipynb) in a Jupyter Notebook while in the qcodes environment and go through the steps (you can run the code on your computer).

Most commands here assume you import the nplab_drivers as follows:

`import qcodes.instrument_drivers.nplab_drivers as npd`

#### Functions from common_commands.py
The biggest addition I made was adding 3 commands that summarize most measurements you would need to do in something similar to electrical transport experiments. It uses the what is described in the QCodes documentation as "legacy qcodes" (the database function has since been updated, but mine uses the old version). 

#### Instrument initialization
The instrumentinitialize file includes the method I use to quickly initialize the machines that I personally use. You can base your initialization off of this framework, but the details will be specific to your setup. `triton_init()` initializes our dilution fridge and other instruments specified by feeding the string codes of the instruments to the `triton_init()` command. Similarly with `ppms_init()`, which initializes the DynaCool ppms system and other instruments connected to it. This is not a verbose method but based on short names I have for the instruments and keeps consistency on a given instrument. It also prevents me from having to copy GPIB addresses when starting a new experiment.

#### Custom instrument drivers
I made a few instrument drivers that are customized to our setup, including the Dynacool PPMS fridge (1.7 to 400 K temperature range, +/- 9 T uniaxial magnet field range) and an Oxford Triton dilution fridge (+/- 8 T uniaxial magnet)

#### Helper commands:
I also added a few functions that I made to help with managing time-based parameters and plotting.


Make sure you're using the qcodes environment when you're opening ipython, spyder, or jupyter sessions, or when you run a file the imports things from the qcodes package.
