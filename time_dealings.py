import qcodes as qc
import time
import numpy as np
import datetime.datetime as datetime
from qcodes import Parameter


class time_from_start(Parameter):
    """ Only a get command, resets the start when initialized and when
    .reset() is called.
    Returns time from last reset in seconds"""
    def __init__(self, name, **kwargs):
        super().__init__(name, get_parser=float, **kwargs)
        self.t0 = time.time()

    def get_raw(self):
        return time.time() - self.t0

    def reset(self):
        self.t0 = time.time()


class time_stamp(Parameter):
    """ Only a get command. Measures time from a set period that python
    can easily interpret into a datetime object or use for interpreting
    into a string date/time"""
    def __init__(self, name, **kwargs):
        super().__init__(name, get_cmd=time.time(),
                         get_parser=float, **kwargs)


def output_date_strings(values, fmt='%Y-%m-%d %H:%M:%S:%f'):
    """ values can be an array of time.time() floats or single time.time()
    floats. Returns a list of strings with the date in the format fmt

    values"""
    if type(values) is float or type(values) is int:
        v = float(values)
    elif type(values) is np.ndarray or type(values) is qc.data.data_array.DataArray:
            v = np.array(values)
    elif type(values) is list:
        if all(type(item) is int or type(item) is float for item in values):
            v = np.array(values)
        else:
            print('input list must be floats or integers')
            return
    dtimearray = []
    for val in v:
        dtimearray.append(datetime.fromtimestamp(val).strftime(fmt))

    return dtimearray
