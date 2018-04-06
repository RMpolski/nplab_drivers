# Commonly used simple loops and calculated parameter structure
import qcodes as qc
from math import ceil
from qcodes.instrument_drivers.nplab_drivers.time_params import time_from_start


def single_param_sweep(SetParam, SetArray, delay, *MeasParams,
                       DataName='', XParam=None, YParam=None,
                       plot_results=True):
    """ Single parameter sweep, single measure (for more measurements, add
    parameters to the .each() part). Includes live plot.

    Returns: data (a qcodes DataSet object), plot

    Arguments:
    SetParam: The parameter to sweep (such as a voltage)
    SetArray: should be a list or numpy array of values you want to set
                SetParam to.
    delay: The delay time between when SetParam is set till the MeasParams
                are measured (0 by default).
    *MeasParam: The comma-separated parameters you want to measure at each
                setpoint
    Keyword Arguments:
    DataName: A name to tag the data (defaults to nothing)
    XParam: Optional, the x parameter to be used in plotting (if not used, will
                default to the set parameter for every plot). Must be either a
                list that is the same length as YParam, a single parameter, or
                None.
    YParam: Allows you to pick only a few parameters to plot out of those
                measured.
    """

    loop = qc.Loop(SetParam[SetArray], delay=delay).each(*MeasParams)
    data = loop.get_data_set(name=DataName)
    if plot_results:
        if XParam is None:
            XParam = SetParam

        if len(MeasParams) == 1:
            plot = qc.QtPlot(getattr(data, str(XParam)+'_set'),
                             getattr(data, str(*MeasParams)),
                             window_title=str(XParam)+' vs. '+str(*MeasParams))
            loop.with_bg_task(plot.update)
        else:
            if YParam is None:
                YParam = MeasParams
            if type(XParam) is not list and type(XParam) is not tuple:
                if type(YParam) is not list and type(YParam) is not tuple:
                    XParam = [XParam]
                    YParam = [YParam]
                else:
                    XParam = [XParam]*len(MeasParams)
            elif len(XParam) != len(YParam):
                raise ValueError('length of XParam list must be the same as' +
                                 'length of YParam list')

            # Create a str for XParam so we can account for _set in the str
            XParamStr = []
            for i in range(len(XParam)):
                xpi = str(XParam[i])
                if xpi == str(SetParam):
                    XParamStr.append(xpi + '_set')
                else:
                    XParamStr.append(xpi)

            plot = []
            for i in range(len(YParam)):
                title = str(YParam[i]) + ' vs. ' + str(XParam[i])
                plot.append(qc.QtPlot(getattr(data, XParamStr[i]),
                            getattr(data, str(YParam[i])), window_title=title))

            def _plot_update():
                for p in plot:
                    p.update()

            def _plot_save():
                for p in plot:
                    p.save()

            loop.with_bg_task(_plot_update, _plot_save)
    loop.run()
    try:
        return data, plot
    except KeyboardInterrupt:
        _plot_update()
        _plot_save()
        return data, plot


def twod_param_sweep(SetParam1, SetArray1, SetParam2, SetArray2, MeasParam,
                     SetDelay1=0, SetDelay2=0, DataName=''):
    """ Single parameter sweep, single measure (for more measurements, add
    parameters to the .each() part). Includes live plot.

    Returns: data (a qcodes DataSet object), plot

    Arguments:
    SetParam1: The outer parameter to sweep (such as a temperature)
    SetArray1: should be a list or numpy array of values you want to set
                SetParam1 to. This array will be run through once
    SetParam2: The inner parameter to sweep (such as a voltage)
    SetArray1: should be a list or numpy array of values you want to set
                SetParam2 to. This array will be run through for each value of
                SetArray1
    MeasParam: The parameter you want to measure at each setpoint
    Keyword Arguments:
    SetDelay1: The delay time between when SetParam1 is set till the SetParam2
                is set to its first value (0 by default)
    SetDelay2: Delay time between when SetParam2 is set and the MeasParam
                is measured (0 by default)
    DataName: A name to tag the data (defaults to nothing)
    """

    twodloop = qc.Loop(SetParam1[SetArray1],
                       delay=SetDelay1).loop(SetParam2[SetArray2],
                                             delay=SetDelay2).each(MeasParam)
    data = twodloop.get_data_set(name=DataName)
    plot = qc.QtPlot(getattr(data, str(MeasParam)))
    twodloop.with_bg_task(plot.update, plot.save).run()
    try:
        return data, plot
    except KeyboardInterrupt:
        plot.update()
        plot.save()
        return data, plot


def data_log(delay, *MeasParams, N=None, minutes=None, DataName='',
             XParam=None, YParam=None, plot_results=True):
    """A loop that takes measurements every "delay" seconds (starts measuring
    at startup, and each delay comes after the measurement). Either choose to
    measure N times or for minutes. The arrays of the data are: count_set
    (the number of the data point), time0 (the time since the start),
    *MeasParams (comma-separated collection of parameters (instr.param)
    measured at each point)

    Note that the amount of minutes may be slightly larger than min because
    this assumes the time of measurement for the parameters is 0.

    Returns: data (a DataSet object), plot (a plot or a list of plots
    if MeasParams has more than one parameter)

    Arguments:
    delay: Seconds between each measurement
    *MeasParams: a comma-separated collection of parameters to measure
    Keyword Arguments:
    N: The number of data points to take (if left None, need to use minutes)
    minutes: The number of minutes to take data points (if left as None, need
                to use N). If minutes/delay is not an integer, rounds up
    DataName: the name to be placed on the file (defaults to '')
    XParam: an optional specification of the x-axis parameter to plot (defaults
            to time0 for all plots). If you want different x-axes for different
            plots, use a list. To include time0 in that list, use the string
            'time' or 'time0'. The list must be the same length as YParam or
            MeasParams
    YParam: optional specification of y-axis parameters to plot (if not
            specified, it will create one plot per MeasParam).
    plot_results: if you want to do the data log without plots, set this to
            False
    """

    count = qc.ManualParameter('count')
    time0 = time_from_start('time0')
    if N is None and minutes is None:
        return ValueError('Must have either N or minutes arguments')
    elif N is not None and minutes is not None:
        return ValueError('Only use N or minutes arguments')
    elif N is not None and minutes is None:
        loop = qc.Loop(count.sweep(1, int(N), step=1)).each(time0,
                                                            *MeasParams,
                                                            qc.Wait(delay))
    elif minutes is not None and N is None:
        N = ceil(minutes*60/delay)
        loop = qc.Loop(count.sweep(1, int(N), step=1)).each(time0,
                                                            *MeasParams,
                                                            qc.Wait(delay))
    data = loop.get_data_set(name=DataName)

    if plot_results:
        if XParam is None:
            XParam = time0

        if len(MeasParams) == 1:
            plot = qc.QtPlot(getattr(data, XParam), getattr(data, *MeasParams),
                             window_title=str(XParam)+' vs. '+str(*MeasParams))
            loop.with_bg_task(plot.update)
        else:
            if YParam is None:
                YParam = MeasParams
            if type(XParam) is not list and type(XParam) is not tuple:
                if type(YParam) is not list and type(YParam) is not tuple:
                    XParam = [XParam]
                    YParam = [YParam]
                else:
                    XParam = [XParam]*len(MeasParams)
            elif len(XParam) != len(YParam):
                raise ValueError('length of XParam list must be the same as' +
                                 'length of YParam list')
            for i in range(len(XParam)):
                if type(XParam[i]) is str:
                    if XParam[i] == 'time' or XParam[i] == 'time0':
                        XParam[i] = time0

            plot = []
            for i in range(len(YParam)):
                title = str(YParam[i]) + ' vs. ' + str(XParam[i])
                plot.append(qc.QtPlot(getattr(data, str(XParam[i])),
                            getattr(data, str(YParam[i])), window_title=title))

            def _plot_update():
                for p in plot:
                    p.update()

            def _plot_save():
                for p in plot:
                    p.save()

            loop.with_bg_task(_plot_update, _plot_save)
    time0.reset()
    loop.run()
    try:
        return data, plot
    except KeyboardInterrupt:
        _plot_update()
        _plot_save()
        return data, plot


# Calculated parameter outline. If the value provided by instr.param() needs
# to have an operation done to it before you want it displayed in the
# measurement, use a parameter defined this way. Define your own function that
# returns what you want, using OhmsfromI as an example.
# constV = 0.5
# def OhmsfromI():
#     return constV/instr.current()
#
#
# paramname = qc.Parameter('paramname', get_cmd=OhmsfromI, label='Resistance',
#                          unit='Ohms')
