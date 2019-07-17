# -*- coding: utf-8 -*-
"""
Created on Thu Jul 04 11:47:28 2019

@author: qde
"""

import numpy             as np
import matplotlib.pyplot as plt
from filterpy.kalman import IMMEstimator
from fdia_simulation.models.radar            import FrequencyRadar
from fdia_simulation.models.tracks           import Track
from fdia_simulation.filters.radar_filter_cv import RadarFilterCV
from fdia_simulation.filters.radar_filter_ca import RadarFilterCA
from fdia_simulation.filters.radar_filter_ct import RadarFilterCT
from fdia_simulation.filters.m_radar_filter  import MultipleFreqRadarsFilter
from fdia_simulation.benchmarks.benchmark    import Benchmark

if __name__ == "__main__":
    #================== Position generation for the aircraft =====================
    trajectory = Track()
    states = trajectory.gen_takeoff()
    x0=states[0,0]
    y0=states[0,3]
    z0=states[0,6]

    dt_rad1 = 0.1
    dt_rad2 = 0.4
    # ==========================================================================
    # ======================== Radars data generation ===========================
    # Radar 1: Precision radar
    radar1 = FrequencyRadar(x = 500, y = 500, dt = dt_rad1)

    # Radar 2: Standard radar
    radar2 = FrequencyRadar(x = 0, y = 1000, dt = dt_rad2,
                            r_noise_std = 5., theta_noise_std = 0.005, phi_noise_std = 0.005)

    # ==========================================================================
    # ========================= IMM generation =================================
    radars = [radar1,radar2]
    radar_filter_cv = MultipleFreqRadarsFilter(dim_x = 9, dim_z = 6, q = 1.,
                                               radars = radars, model = RadarFilterCV,
                                               x0 = x0, y0 = y0, z0 = z0)
    radar_filter_ca = MultipleFreqRadarsFilter(dim_x = 9, dim_z = 6, q = 200.,
                                               radars = radars, model = RadarFilterCA,
                                               x0 = x0, y0 = y0, z0 = z0)
    radar_filter_ct = MultipleFreqRadarsFilter(dim_x = 9, dim_z = 6, q = 350.,
                                               radars = radars, model = RadarFilterCT,
                                               x0 = x0, y0 = y0, z0 = z0)
    filters = [radar_filter_cv, radar_filter_ca, radar_filter_ct]
    mu = [0.33, 0.33, 0.33]
    trans = np.array([[0.998, 0.001, 0.001],
                      [0.050, 0.900, 0.050],
                      [0.001, 0.001, 0.998]])
    imm = IMMEstimator(filters, mu, trans)

    benchmark_imm3 = Benchmark(radars = radars,radar_filter = imm,states = states)
    benchmark_imm3.launch_benchmark(with_nees = True)
