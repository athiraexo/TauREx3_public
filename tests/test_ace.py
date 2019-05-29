import unittest
import numpy as np


class AceChemistryTest(unittest.TestCase):

    def test_compute_profile(self):
        from taurex.data.profiles.chemistry import ACEChemistry
        cgp = ACEChemistry(['H2O','CH4'],spec_file='src/ACE/Data/composes.dat',therm_file='src/ACE/Data/NASA.therm')  
        params = cgp.fitting_parameters()
        test_layers = 10

        cgp.activeGases
        cgp.inActiveGases
        self.assertIsNone(cgp.activeGasMixProfile)
        self.assertIsNone(cgp.inActiveGasMixProfile)
        self.assertIsNone(cgp.muProfile)

        pres_prof = np.ones(test_layers)

        cgp.initialize_chemistry(10,pres_prof,pres_prof,pres_prof)   

        self.assertIsNotNone(cgp.activeGasMixProfile)
        self.assertIsNotNone(cgp.inActiveGasMixProfile)
        self.assertIsNotNone(cgp.muProfile)