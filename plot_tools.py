import qcodes as qc
import numpy as np


def dvdi2dfromiv(dset, instrI, Iparam, instry, yparam, instrV, Vparam,
                 diffset='dVdI'):
    """ V is for voltage, I for current, y is the other parameter (y in 2D).
    It's intended for an I sweep, V measure situation.

    Returns 3 arrays (I, Y, dVdI) or (I, Y, dIdV) that can be used to plot
    using plt.pcolormesh(I, Y, dVdI).

    You can change between dVdI and dIdV using keyword arg diffset
    'dIdV' or 'dVdI'
    """
    Ip = instrI + '_' + Iparam + '_set'
    yp = instry + '_' + yparam + '_set'
    Vp = instrV + '_' + Vparam

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


def concat_2d(dsets, instrx, xparam, instry, yparam, instrz, zparam):
    """Concatenates 2D datasets. When the x direction has been partially measured
    for the top y point and has been replaced by the second array, this
    function replaces the points with the second array and concatenates the two

    dsets must be a tuple, of length 2 or more, of qcodes datasets
    instr(x,y,z) must be the instrument name 'string'
    xparam, yparam, zparam, are the parameter names (strings) used in the
    measurement

    Returns X, Y, Z, numpy arrays that can be plotted with
    plt.pcolormesh(X, Y, Z)

    Note: xparam is for the inner loop sweep, and yparam the outer loop. Also,
    enter the dsets in the order that they were taken.
    Also, you may encounter problems when using plt.pcolormesh due to nan
    values. If you do, just use Z = np.nan_to_num(Z) to replace nans with 0.
    """

    xp = instrx + '_' + xparam + '_set'
    yp = instry + '_' + yparam + '_set'
    zp = instrz + '_' + zparam

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
# def concat_2d_dset(dsets, instrx, xparam, instry, yparam, instrz, zparam):
#     """Concatenates 2D datasets. When the x direction has been partially measured
#     for the top y point and has been replaced by the second array, this
#     function replaces the points with the second array and concatenates the two
#
#     dsets must be a tuple, of length 2 or more, of qcodes datasets
#     instr(x,y,z) must be the instrument name 'string'
#     xparam, yparam, zparam, are the parameter names (strings) used in the
#     measurement
#
#     Note: xparam is for the inner loop sweep, and yparam the outer loop. Also,
#     enter the dsets in the order that they were taken.
#
#     returns a combined dataset with the correct labels, names, and array_ids
#     just like the first dset
#     """
#
#     xp = instrx + '_' + xparam + '_set'
#     yp = instry + '_' + yparam + '_set'
#     zp = instrz + '_' + zparam
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
