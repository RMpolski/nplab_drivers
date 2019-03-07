# functions used to initalize the instruments on each computer
import qcodes as qc

from qcodes.instrument_drivers.tektronix.Keithley_2000 import Keithley_2000
from qcodes.instrument_drivers.nplab_drivers.Keithley_6221 import Keithley_6221
from qcodes.instrument_drivers.nplab_drivers.Keithley_2182a import Keithley_2182a
from qcodes.instrument_drivers.nplab_drivers.Keithley_2200 import Keithley_2200
from qcodes.instrument_drivers.nplab_drivers.QD import QD
from qcodes.instrument_drivers.nplab_drivers.LR_700 import LR_700
from qcodes.instrument_drivers.nplab_drivers.OpenDacs_Seekat import Seekat
from qcodes.instrument_drivers.nplab_drivers.OpenDacs_DAC_ADC import DAC_ADC
from qcodes.instrument_drivers.stanford_research.SR830 import SR830
from qcodes.instrument_drivers.nplab_drivers.vdpArduino import vdpArduino
from qcodes.instrument_drivers.nplab_drivers.NPTriton import Triton
from qcodes.instrument_drivers.nplab_drivers.SR560 import SR560


standardppms = ('k6', 'lockin1')  # ppms always initializes


def ppms_init(*instruments):
    """Enter the instrument codes to initialize each of the following
        instruments (ppms automatically inits as 'ppms'):

        standard: whatever you specify above in the tuple
        k6: keithley 6221
        lockin1: The top lock-in amplifier
        lockin2: The second from top lock-in amplifier
        lr700: The Lakeshore bridge
        k2200: Keithley 2200 voltage source
        k2182: Keithley 2182a nanovoltmeter
        k2015: The standard Keithley 2015 source-meter
        seekat: OpenDacs Seekat
        DAC_ADC: OpenDacs DAC_ADC
        vdp: Daniel's van der pauw switch box"""

    ppms_instrs('ppms')
    for ind, inst in enumerate(instruments):
        if inst.lower() == 'standard':
            for sinstr in standardppms:
                ppms_instrs(sinstr.lower())
            # Put the standard PPMS initialization protocol here
            time.wait(1)
            k6.compliance(0.2)
            k6.AC_phasemark(1)
            k6.AC_phasemark_offset(0)
            instruments = ('ppms', *standardppms, *instruments[i for i in instruments if i.lower() != 'standard'])
        else:
            ppms_instrs(inst.lower())


standardtriton = ('k6', 'lockin')  # triton always initializes


def triton_init(*instruments):
    """Enter the instrument codes (string) to initialize each of the following
        instruments (triton automatically inits as 'triton'):

        standard: whatever you specify directly above in the tuple
        k6: keithley 6221
        lockin: The lock-in amplifier
        sr560: the stanford SR560 voltage pre-amp
        k2200: Keithley 2200 voltage source
        k2182: Keithley 2182a nanovoltmeter
        k2015: The standard Keithley 2015 source-meter
        seekat: OpenDacs Seekat
        DAC_ADC: OpenDacs DAC_ADC
        vdp: Daniel's van der pauw switch box"""

    triton_instrs('triton')
    for ind, inst in enumerate(instruments):
        if inst.lower() == 'standard':
            for sinstr in standardtriton:
                triton_instrs(sinstr.lower())
            # Put the initialization for standard instruments here
            time.wait(1)
            k6.compliance(0.2)
            k6.AC_phasemark(1)
            k6.AC_phasemark_offset(0)
            instruments = ('triton', *standardtriton, *instruments[i for i in instruments if i.lower() != 'standard'])
        else:
            triton_instrs(inst.lower())
            # Put any extra standards here


def ppms_instrs(instr_str):
    if instr_str == 'k6':
        global k6
        k6 = Keithley_6221('k6', 'GPIB::12::INSTR')
    elif instr_str == 'k2182':
        global k2182
        k2182 = Keithley_2182a('k2182', 'GPIB::7::INSTR')
    elif instr_str == 'k2015':
        global k2015
        k2015 = Keithley_2000('k2015', 'GPIB::1::INSTR')
    elif instr_str == 'k2200':
        global k2200
        k2200 = Keithley_2200('k2200', 'GPIB::19::INSTR')
    elif instr_str == 'ppms':
        global ppms
        ppms = QD('ppms')
    elif instr_str == 'seekat':
        global seekat
        seekat = Seekat('seekat', 'COM6', timeout=8)
    elif instr_str == 'dacadc':
        global dacadc
        dacadc = DAC_ADC('dacadc', 'COM9', timeout=8)
    elif instr_str == 'lr700':
        global lr700
        lr700 = LR_700('lr700', 'GPIB::18::INSTR')
    elif instr_str == 'lockin1':
        global lockin1
        lockin1 = SR830('lockin1', 'GPIB0::9::INSTR')
    elif instr_str == 'lockin2':
        global lockin2
        lockin2 = SR830('lockin2', 'GPIB0::8::INSTR')
    elif instr_str == 'vdp':
        global vdp
        vdp = vdpArduino('vdp', 'COM10', timeout=6)


def triton_instrs(instr_str):
    if instr_str == 'triton':
        global triton
        triton = Triton('triton', 'triton.local', 33576)
    if instr_str == 'k6':
        global k6
    elif instr_str == 'k2182':
        global k2182
        k2182 = Keithley_2182a('k2182', 'GPIB::7::INSTR')
    elif instr_str == 'k2015':
        global k2015
        k2015 = Keithley_2000('k2015', 'GPIB::1::INSTR')
    elif instr_str == 'k2200':
        global k2200
        k2200 = Keithley_2200('k2200', 'GPIB::19::INSTR')
    elif instr_str == 'seekat':
        global seekat
        seekat = Seekat('seekat', 'COM6', timeout=8)
    elif instr_str == 'dacadc':
        global dacadc
        dacadc = DAC_ADC('dacadc', 'COM9', timeout=8)
    elif instr_str == 'lockin':
        global lockin
        lockin1 = SR830('lockin', 'GPIB0::8::INSTR')
    elif instr_str == 'vdp':
        global vdp
        vdp = vdpArduino('vdp', 'COM10', timeout=6)
    elif instr_str == 'sr560':
        global sr560
        sr560 = SR560('sr560', 'COM5')
