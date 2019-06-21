# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 13:07:46 2019

@author: qde
"""

import numpy as np
import matplotlib.pyplot as plt
from math import cos,sin,sqrt
from fdia_simulation.models.moving_target import MovingTarget, Command, NoisySensor
from fdia_simulation.models.maneuvered_aircraft import ManeuveredAircraft

class Radar(object):
    r'''Implements a simulated radar.
    The radar will output a data set corresponding to typical radar values.
    Attributes
    ----------
    r_noise_std: float
        Standard deviation on the measurement of r. Default value of 1.

    theta_noise_std: float
        Standard deviation on the measurement of theta. Default value of 0.1

    phi_noise_std: float
        Standard deviation on the measurement of phi. Default value of 0.1

    Parameters
    ----------
    Identical to Attributes
    '''

    def __init__(self, r_noise_std = 1., theta_noise_std = 0.01, phi_noise_std = 0.01):
            self.r_noise_std      = r_noise_std
            self.theta_noise_std  = theta_noise_std
            self.phi_noise_std    = phi_noise_std

    def gen_data(self,position_data):
        '''
        Generates simulated received data for a radar.
        Parameters
        ----------
        position_data: float list numpy array
            List of positions in the form of lists [x_k, y_k, z_k].
            Corresponding to:
            x_k: float
                Position following x-axis.

            y_k: float
                Position following y-axis.

            z_k: float
                Position following z-axis.

        Returns
        -------
        sensed_values: float list numpy array
            List of radar sensed values in the form of lists [r_k, theta_k, phi_k].
            Corresponding to:
            r_k: float
                Range, distance of the target.

            theta_k: float
                Azimuth angle (turning angle).

            phi_k: float
                Elevation angle.
        '''
        xs = position_data[:,0]
        ys = position_data[:,1]
        zs = position_data[:,2]
        rs, thetas, phis = [], [], []

        for k in range(len(position_data)):
            r_k     = sqrt(xs[k]**2 + ys[k]**2 + zs[k]**2)
            theta_k = np.arctan(ys[k]/xs[k])
            phi_k   = np.arctan(zs[k]/ sqrt(xs[k]**2 + ys[k]**2))

            rs.append(r_k)
            thetas.append(theta_k)
            phis.append(phi_k)

        radar_values = np.array(list(zip(rs,thetas,phis)))

        nsr     = NoisySensor(self.r_noise_std)
        nstheta = NoisySensor(self.theta_noise_std)
        nsphi   = NoisySensor(self.phi_noise_std)

        noisy_rs     = [nsr.sense(r) for r in rs]
        noisy_thetas = [nstheta.sense(theta) for theta in thetas]
        noisy_phis   = [nsphi.sense(phi) for phi in phis]

        return noisy_rs,noisy_thetas,noisy_phis

    def radar2cartesian(self,rs,thetas,phis):
        xs,ys,zs = [],[],[]
        for k in range(len(rs)):
            x_k = rs[k] * cos(thetas[k]) * cos(phis[k])
            y_k = rs[k] * sin(thetas[k]) * cos(phis[k])
            z_k = rs[k] * sin(phis[k])

            xs.append(x_k)
            ys.append(y_k)
            zs.append(z_k)

        return xs,ys,zs

if __name__ == "__main__":
    #================== Position generation for the aircraft =====================
    # Route generation example with a ManeuveredBicycle
    sensor_std = 1.
    headx_cmd = Command('headx',0,0,0)
    headz_cmd = Command('headz',0,0,0)
    vel_cmd   = Command('vel',1,0,0)
    aircraft  = ManeuveredAircraft(x0 = 1, y0 = 1, z0=1, v0 = 0, hx0 = 0, hz0 = 0, command_list = [headx_cmd, headz_cmd, vel_cmd])
    xs, ys, zs = [], [], []

    # Take off acceleration objective
    aircraft.change_command("vel",200, 20)
    # First phase -> Acceleration
    for i in range(10):
        x, y, z = aircraft.update()
        xs.append(x)
        ys.append(y)
        zs.append(z)

    # Change in commands -> Take off
    aircraft.change_command("headx",315, 25)
    aircraft.change_command("headz",315, 25)

    # Second phase -> Take off
    for i in range(30):
        x, y, z = aircraft.update()
        xs.append(x)
        ys.append(y)
        zs.append(z)

    # Change in commands -> Steady state
    aircraft.change_command("headx",90, 25)
    aircraft.change_command("headz",270, 25)

    # Third phase -> Steady state
    for i in range(60):
        x, y, z = aircraft.update()
        xs.append(x)
        ys.append(y)
        zs.append(z)

    position_data = np.array(list(zip(xs,ys,zs)))

    # ================= Radar generation ======================

    radar = Radar()
    noisy_rs, noisy_thetas, noisy_phis = radar.gen_data(position_data)
    xs_from_rad, ys_from_rad, zs_from_rad = radar.radar2cartesian(noisy_rs, noisy_thetas, noisy_phis)

    radar_values = np.array(list(zip(noisy_rs, noisy_thetas, noisy_phis)))
    print(radar_values)

    radar_computed_values = np.array(list(zip(xs_from_rad, ys_from_rad, zs_from_rad)))
    print(radar_computed_values)

    # ================ Plotting ====================

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.plot(xs, ys, zs, label='plot test',color='k',linestyle='dashed')
    ax.scatter(xs_from_rad, ys_from_rad, zs_from_rad,color='b',marker='o')
    plt.show()
