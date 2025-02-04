# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 09:18:23 2019

@author: qde
"""

import warnings
import numpy as np
from filterpy.kalman import IMMEstimator

class Attacker(object):
    '''
    Implements a basic attacker model.
    Parameters
    ----------
    filter: ExtendedKalmanFilter
        Filter of the attacked system.

    gamma: int numpy array
        Attack matrix: Diagonal square matrix with n = measurement (z) dimension.
        Terms on the diagonal are either equal to 0 (no attack on this parameter)
        or 1 (attack on the parameter).
        Example: 2 radars
         np.array([[0, 0, 0, 0, 0, 0],  <--- No attack on r1
                   [0, 0, 0, 0, 0, 0],  <--- No attack on theta1
                   [0, 0, 0, 0, 0, 0],  <--- No attack on phi1
                   [0, 0, 0, 1, 0, 0],  <--- Attack on r2    )
                   [0, 0, 0, 0, 1, 0],  <--- Attack on theta2 } Attack on radar2
                   [0, 0, 0, 0, 0, 1]]) <--- Attack on phi2  )

    mag_vector: float numpy array
        Attack magnitude vector. The attack will consist of adding the quantity
        Gamma@mag_vector to the actual measurements.

    t0: float
        Time of beginning of the attack.

    time: int
        Duration of the attack (number of update steps)

    Attributes
    ----------
    Same as parameters +
    dim_z: int
        Dimension of the measurements.

    current_time: int
        Progression of the attack (from t0 to time)
    '''
    def __init__(self, filter, t0, time, radar,
                 gamma = None, mag_vector = None, radar_pos = None):
        # Store the filter and its dimension
        self.filter = filter
        self.is_imm = isinstance(filter,IMMEstimator)
        if self.is_imm:
            self.dim_z  = filter.filters[0].dim_z
        else:
            self.dim_z = filter.dim_z
        self.radar  = radar
        # print('dim_z = {0}'.format(dim_z))

        # If gamma is not specified but the attacked radar position (in the
        # measurement matrix) is
        if (gamma is None) and not(radar_pos is None):
            gamma = np.zeros((self.dim_z,self.dim_z))
            gamma[radar_pos*3  , radar_pos*3]   = 1 # Attacked r
            gamma[radar_pos*3+1, radar_pos*3+1] = 1 # Attacked theta
            gamma[radar_pos*3+2, radar_pos*3+2] = 1 # Attacked phi

        # If the magnitude vector is not specified but the attacked radar position
        # (in the measurement matrix) is
        if (mag_vector is None) and not(radar_pos is None):
            mag_vector = np.zeros((self.dim_z,1))
            mag_vector[radar_pos*3    , 0] = 1
            mag_vector[radar_pos*3 + 1, 0] = 1
            mag_vector[radar_pos*3 + 2, 0] = 1

        # The attack matrix should be a squared matrix with n = dim_z
        if np.shape(gamma) != (self.dim_z,self.dim_z):
            raise ValueError('Gamma should be a square matrix with n=dim_z')

        if np.shape(mag_vector) != (self.dim_z,1):
            msg = """The magnitude vector should have the following dimensions:
                     (dim_z,1) with dim_z = {0} here""".format(self.dim_z)
            raise ValueError(msg)


        self.gamma       = gamma
        self.mag_vector  = mag_vector

        # If the attackers input is null, the attack will have no effect
        if np.array_equal(self.gamma@self.mag_vector,np.zeros((self.dim_z,1))):
            msg = """With the current attack matrix (gamma) and magnitude vector,
                     your attack will have no effect"""
            warnings.warn(msg,Warning)

        # Time attributes
        self.t0           = t0
        self.time         = time
        self.current_time = 0

    def attack_measurement(self, measurement):
        '''
        Performs the attack on a given measurement. It simply consists of adding
        to that measurement the quantity gamma@mag_vector. This means you are
        specifying which parameters are modified in gamma (which radar is attacked)
        and with what magnitude in the magnitude vector.
        Parameters
        ----------
        measurement: float numpy array
            Measurement as outputed by the radar under attack.

        Returns
        -------
        modified_z: float numpy array (dim_z,1)
            Modified measurement consisting of:
            Initial measurement + Gamma * Magnitude vector
        '''
        modified_measurement = measurement + self.gamma@self.mag_vector
        return modified_measurement

    def listen_measurement(self,measurement):
        '''
        Monitors the duration (beginning and end) of the attack.
        Parameters
        ----------
        measurement: float numpy array
            Measurement
        '''
        beginning_reached = self.t0 <= self.current_time
        end_reached       = (self.current_time - self.t0) >= self.time
        if beginning_reached and not(end_reached):
            measurement = np.reshape(measurement,(-(self.dim_z-1),1))
            measurement = self.attack_measurement(measurement)
        self.current_time += 1
        return measurement
