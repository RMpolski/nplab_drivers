from qcodes import VisaInstrument
import qcodes.utils.validators as vals


def R_parser(string_out):
    newstrs = string_out.strip().split(' ')

    if newstrs[1] == 'KOHM':  # kilo Ohms
        return float(newstrs[0])*10e3
    elif newstrs[1] == 'MOHM':
        return float(newstrs[0])*10e-3  # I think this is probably milli Ohms
    elif newstrs[1] == 'UOHM':  # micro Ohms
        return float(newstrs[0])*10e-6
    else:
        return float(newstrs[0])


class LR_700(VisaInstrument):
    """Instrument driver for the Lakeshore LR_700 AC resistance bridge.
    Currently only has the ability to get resistance, set the full-scale
    resistance measurement range, autorange (on 1, off 0), and set the
    excitation voltage.
    Note: You need to input the exact excitation voltage (in V) and range
    (in ohms). You can find the allowed values in the parameters
    self.range_vals and self.excitation_vals.

    exc_pct: selects a value for the percent of the full excitation to output
    exc_pct_on: 0 sets to 100 pct excitation. 1 sets to the exc_pct value
    """
    def __init__(self, name: str, address: str, **kwargs):
        super().__init__(name, address, terminator='\n', **kwargs)

        self.range_vals = {2e-3: 0, 20e-3: 1, 200e-3: 2, 2: 3,
                           20: 4, 200: 5, 2e3: 6, 20e3: 7, 200e3: 8,
                           2e6: 9}
        self.excitation_vals = {20e-6: 0, 60e-6: 1, 200e-6: 2,
                                600e-6: 3, 2e-3: 4, 6e-3: 5, 20e-3: 6}

        self.add_parameter('range',
                           set_cmd='Range {}',
                           val_mapping=self.range_vals)
        self.add_parameter('autorange',
                           set_cmd='Autorange {}',
                           vals=vals.Ints(0, 1))
        self.add_parameter('excitation',
                           set_cmd='Excitation {}',
                           val_mapping=self.excitation_vals)
        self.add_parameter('exc_pct',
                           set_cmd='Varexc ={}',
                           vals=vals.Ints(5, 99))
        self.add_parameter('exc_pct_on',
                           set_cmd='Varexc {}',
                           vals=vals.Ints(0, 1))
        self.add_parameter('R_measure',
                           get_cmd='Get 0',
                           get_parser=R_parser)
        self.add_parameter('X_measure',
                           get_cmd='Get 1',
                           get_parser=R_parser)
