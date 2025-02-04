# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 14:07:21 2019

@author: qde
"""

import numpy as np
from copy import deepcopy
from fdia_simulation.attackers import PeriodAttacker,DOSAttacker,DriftAttacker,CumulativeDriftAttacker

class DOSPeriodAttacker(PeriodAttacker,DOSAttacker):
    '''
    Implements an attack strategy consisting of systematically giving out wrong
    measurements in order to make the filter condemn the attacked sensor. This
    attack is not stealthy and can have little to no impact if there are several
    other sensors observing the system.
    Parameters
    ----------
    mag: float
        The magnitude added to the magnitude vector in order to make it always be
        detected by the fault detector.

    + same than Attacker
    '''
    def __init__(self,mag = 1e4,*args,**kwargs):
        PeriodAttacker.__init__(self,*args,**kwargs)
        self.mag_vector = self.mag_vector*mag

    def listen_measurement(self,measurement):
        return PeriodAttacker.listen_measurement(self,measurement)

    def attack_measurement(self,measurement):
        return DOSAttacker.attack_measurement(self,measurement)

class DriftPeriodAttacker(PeriodAttacker,DriftAttacker):
    '''
    Implements an attack strategy consisting of injecting measurements to make
    one to three directional parameter drifting.
    Parameters
    ----------
    attack_drift:  float numpy array (3,1)
        Impact of the attack on the three position parameters.
    '''
    def __init__(self, attack_drift = None, *args, **kwargs):
        if attack_drift is None:
            attack_drift = np.array([[0,0,10]]).T
        self.attack_drift = attack_drift
        PeriodAttacker.__init__(self,*args,**kwargs)

    def listen_measurement(self,measurement):
        return PeriodAttacker.listen_measurement(self,measurement)

    def attack_measurement(self,measurement):
        return DriftAttacker.attack_measurement(self,measurement)

class CumulativeDriftPeriodAttacker(PeriodAttacker,CumulativeDriftAttacker):
    '''
    Implements an attack strategy consisting of injecting measurements to make
    one to three directional parameter drifting.
    Parameters
    ----------
    attack_drift:  float numpy array (3,1)
        Impact of the attack on the three position parameters.
    '''
    def __init__(self,delta_drift = None, *args, **kwargs):
        if delta_drift is None:
            delta_drift = np.array([[0,0,1]]).T
        self.delta_drift  = delta_drift
        self.attack_drift = deepcopy(delta_drift)
        PeriodAttacker.__init__(self,*args,**kwargs)

    def listen_measurement(self,measurement):
        return PeriodAttacker.listen_measurement(self,measurement)

    def attack_measurement(self,measurement):
        return CumulativeDriftAttacker.attack_measurement(self,measurement)
