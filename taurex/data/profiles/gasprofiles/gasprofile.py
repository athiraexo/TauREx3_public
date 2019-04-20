from taurex.log import Logger
from taurex.util import get_molecular_weight,molecule_texlabel
from taurex.data.fittable import fitparam,Fittable
import numpy as np
import math
class GasProfile(Fittable,Logger):
    """
    Defines gas profiles

    """

    


    def __init__(self,name,mode='linear'):
        Logger.__init__(self,name)
        Fittable.__init__(self)
        self.active_mixratio_profile = None
        self.inactive_mixratio_profile = None

        self.active_gases = []
        self.inactive_gases = []
        self.mu_profile = None
        self.setLinearLogMode(mode)
    
    def setLinearLogMode(self,value):
        value = value.lower()
        if value in ('linear','log',):
            self._log_mode =  (value == 'log')
        else:
            raise AttributeError('Linear/Log Mode muse be either \'linear\' or \'log\'')

    @property
    def isInLogMode(self):
        return self._log_mode


    def readableValue(self,value):
        """Helper function to convert the read value to either linear or log space"""

        if self.isInLogMode:
            return math.log10(value)
        else:
            return value
    
    def writeableValue(self,value):
        """Write value back to linear space when in either log or linear mode"""
        if self.isInLogMode:
            return math.pow(10,value)
        else:
            return value

    def initialize_profile(self,nlayers,temperature_profile,pressure_profile,altitude_profile):
        self.nlayers=nlayers
        self.nlevels = nlayers+1
        self.pressure_profile = pressure_profile
        self.temperature_profile = temperature_profile
        self.altitude_profile = altitude_profile

        

        self.compute_active_gas_profile()
        self.compute_inactive_gas_profile()
        self.compute_mu_profile()
    def compute_active_gas_profile(self):
        raise NotImplementedError
    
    def compute_inactive_gas_profile(self):
        raise NotImplementedError

    def compute_mu_profile(self):
        self.mu_profile= np.zeros(shape=(self.nlayers,))
        if self.activeGasMixProfile is not None:
            for idx, gasname in enumerate(self.active_gases):
                self.mu_profile += self.activeGasMixProfile[idx,:]*get_molecular_weight(gasname)
        if self.inActiveGasMixProfile is not None:
            for idx, gasname in enumerate(self.inactive_gases):
                self.mu_profile += self.inActiveGasMixProfile[idx,:]*get_molecular_weight(gasname)
    @property
    def activeGasMixProfile(self):
        return self.active_mixratio_profile

    @property
    def inActiveGasMixProfile(self):
        return self.inactive_mixratio_profile

    @property
    def muProfile(self):
        return self.mu_profile

class TaurexGasProfile(GasProfile):




    def __init__(self,name,active_gases,active_gas_mix_ratio,n2_mix_ratio=0,he_h2_ratio=0.17647,mode='linear'):
        super().__init__(name,mode=mode)
        self.active_gases = active_gases
        self.inactive_gases = ['H2', 'HE', 'N2']
        self.active_gas_mix_ratio = active_gas_mix_ratio
        self._n2_mix_ratio = n2_mix_ratio
        self._he_h2_mix_ratio = he_h2_ratio
    

    def compute_active_gas_profile(self):
        self.active_mixratio_profile=np.zeros((len(self.active_gases), self.nlayers))
        for idx,ratio in enumerate(self.active_gas_mix_ratio):
            self.active_mixratio_profile[idx, :] = ratio
    

    @fitparam(param_name='N2',param_latex=molecule_texlabel('N2'),default_fit=False,default_bounds=[1e-12,1.0])
    def N2MixRatio(self):
        return self.readableValue(self._n2_mix_ratio)
    
    @N2MixRatio.setter
    def N2MixRatio(self,value):
        self._n2_mix_ratio = self.writeableValue(value)

    @fitparam(param_name='H2_He',param_latex=molecule_texlabel('H$_2$/He'),default_fit=False,default_bounds=[1e-12,1.0])
    def H2HeMixRatio(self):
        return self.readableValue(self._he_h2_mix_ratio)
    
    @H2HeMixRatio.setter
    def H2HeMixRatio(self,value):
        self._he_h2_mix_ratio = self.writeableValue(value)


    def compute_inactive_gas_profile(self):

        self.inactive_mixratio_profile = np.zeros((len(self.inactive_gases), self.nlayers))
        self.inactive_mixratio_profile[2, :] = self._n2_mix_ratio
        # first get the sum of the mixing ratio of all active gases
        if len(self.active_gases) > 1:
            active_mixratio_sum = np.sum(self.active_mixratio_profile, axis = 0)
        else:
            active_mixratio_sum = np.copy(self.active_mixratio_profile)
        
        active_mixratio_sum += self.inactive_mixratio_profile[2, :]
        
        mixratio_remainder = 1. - active_mixratio_sum
        self.inactive_mixratio_profile[0, :] = mixratio_remainder/(1. + self._he_h2_mix_ratio) # H2
        self.inactive_mixratio_profile[1, :] =  self._he_h2_mix_ratio * self.inactive_mixratio_profile[0, :] 


    def add_active_gas_param(self,idx):
        mol_name = self.active_gases[idx]

        param_name = mol_name
        param_tex = molecule_texlabel(mol_name)
        if self.isInLogMode:
            param_name = 'log_{}'.format(mol_name)
            param_tex = 'log({})'.format(molecule_texlabel(mol_name))
        
        def read_mol(self):
            return self.readableValue(self.active_gas_mix_ratio[idx])
        def write_mol(self,value):
            self.active_gas_mix_ratio[idx] = self.writeableValue(value)

        fget = read_mol
        fset = write_mol
        
        bounds = [1.0e-12, 0.1]
        if self.isInLogMode:
            bounds=[-12,-1]
        
        default_fit = False
        self.add_fittable_param(param_name,param_tex,fget,fset,default_fit,bounds)  