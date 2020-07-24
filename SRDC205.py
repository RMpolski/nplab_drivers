from qcodes import Instrument
import qcodes.utils.validators as vals
from qcodes.utils.helpers import strip_attrs
import serial
import time
from functools import partial
import numpy as np

boolcheck = (0, 1, 'on', 'off', 'ON', 'OFF', False, True)

def parse_inp_bool(value):
    if type(value) is float:
        value = int(value)
    elif type(value) is str:
        value = value.lower()

    if value in {1, 'on', True}:
        return 1
    elif value in {0, 'off', False}:
        return 0
    else:
        print(value)
        raise ValueError('Must be boolean, on or off, 0 or 1, True or False')

class SRDC205(Instrument):
    """ The Stanford research systems Model DC205 DC voltage source driver
    Address on mac: dev/tty.usbserial-AL05R7UA.
    On windows, some COM port, likely.
    """

    def __init__(self, name, address, timeout=8, **kwargs):
        super().__init__(name, **kwargs)

        self.address = address
        self.terminator = '\n'
        self._open_serial_connection(timeout)

        self.add_parameter(name='volt', get_cmd='VOLT?',
                           set_cmd='VOLT {}',
                           get_parser=float,
                           set_parser=self.voltsetparse,
                           vals=vals.Numbers(-100, 100))
        self.add_parameter(name='range', get_cmd='RNGE?',
                           set_cmd='RNGE {}',
                           get_parser=int,
                           set_parser=int, vals=vals.Ints(0, 2))
        self.add_parameter(name='output', get_cmd='SOUT?',
                           set_cmd='SOUT {}',
                           set_parser=parse_inp_bool,
                           get_parser=int,
                           vals=vals.Enum(*boolcheck))
        self.add_parameter(name='isolation',
                           get_cmd='ISOL?',
                           set_cmd='ISOL {}',
                           set_parser=int,
                           get_parser=int,
                           vals=vals.Ints(0, 1))

        self.connect_message()



    def _open_serial_connection(self, timeout=None):
        if timeout is None:
            ser = serial.Serial(self.address, 115200)
        else:
            ser = serial.Serial(self.address, 115200, timeout=timeout)
        if not (ser.isOpen()):
            ser.open()
        self._ser = ser

    def close(self):
        """Irreversibly stop this instrument and free its resources.
        Closes the serial connection too"""
        if hasattr(self, 'connection') and hasattr(self.connection, 'close'):
            self.connection.close()
        ser = self._ser
        ser.close()

        strip_attrs(self, whitelist=['name'])
        self.remove_instance(self)

    def get_idn(self):
        """ The idn for this instrument also comes from the *IDN command, but
        it needs a \n endline character, and it only returns the instrument
        name"""
        idstr = ''  # in case self.ask fails
        try:
            self._ser.write('*IDN?\n'.encode('utf-8'))
            idstr = self._ser.readline().decode('utf-8').strip()
            # form is supposed to be comma-separated, but we've seen
            # other separators occasionally
            idparts: List[Optional[str]]
            for separator in ',;:':
                # split into no more than 4 parts, so we don't lose info
                idparts = [p.strip() for p in idstr.split(separator, 3)]
                if len(idparts) > 1:
                    break
            # in case parts at the end are missing, fill in None
            if len(idparts) < 4:
                idparts += [None] * (4 - len(idparts))
        except:
            self.log.debug('Error getting or interpreting *IDN?: '
                           + repr(idstr))
            idparts = [None, self.name, None, None]

        # some strings include the word 'model' at the front of model
        if str(idparts[1]).lower().startswith('model'):
            idparts[1] = str(idparts[1])[5:].strip()

        return dict(zip(('vendor', 'model', 'serial', 'firmware'), idparts))

    def ask_raw(self, cmd):
        cmd += self.terminator
        self._ser.write(cmd.encode('utf-8'))
        return self._ser.readline().decode('utf-8').strip()

    def write_raw(self, cmd):
        cmd += self.terminator
        self._ser.write(cmd.encode('utf-8'))

    ## method that's a little bulkier and less functional but still works
    ## use partial(getval/setval, cmdstring)
    # def getval(self, getstring):
    #     s = getstring + '\n'
    #     self._ser.write(s.encode('utf-8'))
    #     return self._ser.readline().decode('utf-8').strip()
    #
    # def setval(self, setstring, val):
    #     s = setstring + ' ' + str(val) + '\n'
    #     self._ser.write(s.encode('utf-8'))

    def voltsetparse(self, val):
        return np.round(float(val), 7)
