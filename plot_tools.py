import qcodes as qc
import pandas as pd
import numpy as np
from scipy.integrate import cumtrapz


def mov_average(array, window):
    """A simple moving average function with a window size. Calculates the
    average of the first number of points in the window, shifts by one point,
    calculates the average, and so on until the end of the array.

    array: the array from which to calculate the moving average
    window: (must be integer) the amount of points in each average
    """
    return np.convolve(array, np.ones((window,))/window, mode='valid')


def find_closest(value, array):
    """Find the closest value to what is in the array and return the
    index. In case of a tie, it chooses the first number"""
    closest = np.argmin(np.abs(array-value))
    return closest


def val_to_index(valuefindarray, array):
    """Searches in array for the values in valuefindarray. Returns a list of
    indices.
    If the value isn't in the array, uses the closest value"""
    indarray = list([])
    count = 0
    for i in valuefindarray:
        if np.isin(i, array):
            indarray.append(list(array).index(i))
        else:
            print('{:.2f} is not a value in the array'.format(i))
            indarray.append(find_closest(i, array))
            print('Plotted {:.2f} instead'.format(array[int(indarray[count])]))
        count += 1
    return indarray


def iv_from_dvdi(dvdi, x, axis=1):
    """ Returns a cumulative integral array from a 2d array dvdi, integrating
    each row by default (choose axis=0 for integrating over columns) and
    somewhat artificially sets the 0 point of x to the 0 point of V"""

    V = cumtrapz(dvdi, x=x, axis=axis, initial=0)

    return V - V[:, val_to_index([0], x)]


def get2d_dat(filename):
    """Gets 2D data from qcodes .dat file.
    Returns X, Y, Z where X and Y are the inner- and outer-loop set params,
    and Z is the measured array"""
    data = pd.read_csv(filename, sep='\t', header=None, comment='#',
                       skip_blank_lines=True)
    npdata = np.array(data)
    Y = np.unique(npdata[:, 0])
    X = npdata[:, 1][np.where(npdata[:, 0] == Y[0])]
    zl = []
    for yval in Y:
        zl.append(npdata[:, 2][np.where(npdata[:, 0] == yval)])
    Z = np.array(zl)
    return X, Y, Z


def dvdi2dfromiv(dset, Iparam, yparam, Vparam, diffset='dVdI'):
    """ V is for voltage, I for current, y is the other parameter (y in 2D).
    It's intended for an I sweep, V measure situation.

    Note: this is for
    calculating dV/dI or dI/dV when current is the swept parameter and voltage
    is measured.

    Iparam, yparam, Vparam are the parameters (instr.param) used in acquiring
    the datasets dset.

    Returns 3 arrays (I, Y, dVdI) or (I, Y, dIdV) that can be used to plot
    using plt.pcolormesh(I, Y, dVdI).

    You can change between dVdI and dIdV using keyword arg diffset
    'dIdV' or 'dVdI' (not case sensitive)
    """
    Ip = str(Iparam) + '_set'
    yp = str(yparam) + '_set'
    Vp = str(Vparam)

    curr = getattr(dset, Ip)[0]
    Y = getattr(dset, yp).ndarray
    dI = np.gradient(curr)
    dV = np.gradient(getattr(dset, Vp).ndarray, axis=1)

    if diffset.lower() == 'dvdi':
        dVdI = dV/dI
        return curr, Y, dVdI
    elif diffset.lower() == 'didv':
        dIdV = dI/dV
        return curr, Y, dIdV
    else:
        raise ValueError('diffset keyword arg must be either dVdI or dIdV' +
                         ' upper or lowercase')


def concat_2d(dsets, xparam, yparam, zparam):
    """Concatenates 2D datasets. When the x direction has been partially measured
    for the top y point and has been replaced by the second array, this
    function replaces the points with the second array and concatenates the two

    dsets must be a tuple, of length 2 or more, of qcodes datasets
    xparam, yparam, zparam, are the parameters (instrument.param) used in the
    measurement

    Returns X, Y, Z, numpy arrays that can be plotted with
    plt.pcolormesh(X, Y, Z)

    Note: xparam is for the inner loop sweep, and yparam the outer loop. Also,
    enter the dsets in the order that they were taken.
    Also, you may encounter problems when using plt.pcolormesh due to nan
    values. If you do, just use Z = np.nan_to_num(Z) to replace nans with 0.
    """

    xp = str(xparam) + '_set'
    yp = str(yparam) + '_set'
    zp = str(zparam)

    if len(dsets) < 2:
        raise ValueError('Need tuple of length >=2 for argument')

    # Check for same x shapes
    for a in dsets[1:len(dsets)]:
        if getattr(a, xp).shape[1] != getattr(dsets[0], xp).shape[1]:
                raise ValueError('Datasets must have same length in x')

    X = getattr(dsets[0], xp)[0]

    # initialize yfinalvals with first dset and work forward
    # also initialize z until first nan or end of first dset
    # First toss these in one by one and then sort at the end
    yfinalvals = []
    zfinalvals = []
    y0vals = getattr(dsets[0], yp).ndarray

    for yind in range(0, len(y0vals)):
        if np.isnan(y0vals[yind]):
            break
        else:
            yfinalvals.append(y0vals[yind])
            zfinalvals.append(getattr(dsets[0], zp)[yind])

    # Concatenate the y values
    for d in dsets[1:]:
        new_yvals = getattr(d, yp).ndarray
        for vind in range(0, len(new_yvals)):
            val = new_yvals[vind]
            if np.isnan(val):
                break
            elif val in yfinalvals:
                ind = yfinalvals.index(val)
                zfinalvals[ind] = getattr(d, zp)[vind]
            else:
                zfinalvals.append(getattr(d, zp)[vind])
                yfinalvals.append(val)

    indsort = np.array(yfinalvals).argsort()
    Y = np.array(yfinalvals)
    Y.sort()
    Z = np.array(zfinalvals)[indsort]

    return X, Y, Z


# TODO: Make these functions work with datasets: below
# def concat_2d_dset(dsets, xparam, yparam, zparam):
#     """Concatenates 2D datasets. When the x direction has been partially measured
#     for the top y point and has been replaced by the second array, this
#     function replaces the points with the second array and concatenates the two
#
#     dsets must be a tuple, of length 2 or more, of qcodes datasets
#     xparam, yparam, zparam, are the parameter names (instr.param) used in the
#     measurement
#
#     Note: xparam is for the inner loop sweep, and yparam the outer loop. Also,
#     enter the dsets in the order that they were taken.
#
#     returns a combined dataset with the correct labels, names, and array_ids
#     just like the first dset
#     """
#
#     xp = str(xparam) + '_set'
#     yp = str(yparam) + '_set'
#     zp = str(zparam)
#
#     if len(dsets) < 2:
#         raise ValueError('Need tuple of length >=2 for argument')
#
#     # Check for same x shapes
#     for a in dsets[1:len(dsets)]:
#         if getattr(a, xp).shape[1] != getattr(dsets[0], xp).shape[1]:
#                 raise ValueError('Datasets must have same length in x')
#
#     cdata = qc.new_data()
#
#     # TODO: Introduce ypvals here straight from the arrays and then update them
#     # in the loop continuously
#
#     yfinalvals = []
#
#     npdsetsx = []
#     npdsetsz = []
#     for i in range(0, len(dsets)-1):
#         nextarray = False
#         for j in range(0, len(getattr(dsets[i], yp))):
#             ypval = getattr(dsets[i], yp)[j]
#             if (ypval in getattr(dsets[i+1], yp) or ypval is np.nan) and \
#                     nextarray is False:
#                     # If this point is in the next array, append the array up
#                     # to that point and append the next array
#                 yfinalvals.append(getattr(dsets[i], yp)[0:j])
#
#                 npdsetsx.append(getattr(dsets[i], xp)[0:j])
#                 npdsetsz.append(getattr(dsets[i], zp)[0:j])
#
#                 npdsetsx[i].append(*getattr(dsets[i+1], xp))
#                 npdsetsz[i].append(*getattr(dsets[i+1], zp))
#                 nextarray = True
#             elif nextarray is True and ypval is np.nan:
#                 # if nan, break. No more values to search for
#                 break
#             elif nextarray is False and j == len(getattr(dsets[i], yp))-1:
#                 # if the end of the array and no match, append the next array
#                 npdsetsx.append(getattr(dsets[i], xp))
#                 npdsetsy.append(getattr(dsets[i], yp))
#                 npdsetsz.append(getattr(dsets[i], zp))
#
#                 npdsetsx[i].append(*getattr(dsets[i+1], xp))
#                 npdsetsy[i].append(*getattr(dsets[i+1], yp))
#                 npdsetsz[i].append(*getattr(dsets[i+1], zp))
#
#             elif nextarray is True and ypval not in getattr(dsets[i+1], yp):
#                 # if the next array is already appended, and there are values
#                 # not in that array, append them
#                 npdsetsx[i].append(getattr(dsets[i], xp)[j])
#                 npdsetsy[i].append(getattr(dsets[i], yp)[j])
#                 npdsetsz[i].append(getattr(dsets[i], zp)[j])
#
#     # Assign dataset attributes to new dataset arrays
#     aidx = getattr(dsets[0], xp).array_id
#     aidy = getattr(dsets[0], yp).array_id
#     aidz = getattr(dsets[0], zp).array_id
#     anamex = getattr(dsets[0], xp).name
#     anamey = getattr(dsets[0], yp).name
#     anamez = getattr(dsets[0], zp).name
#     alabelx = getattr(dsets[0], xp).label
#     alabely = getattr(dsets[0], yp).label
#     alabelz = getattr(dsets[0], zp).label
#     aunitx = getattr(dsets[0], xp).unit
#     aunity = getattr(dsets[0], yp).unit
#     aunitz = getattr(dsets[0], zp).unit
