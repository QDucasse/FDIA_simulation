# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 13:45:53 2019

@author: qde
"""

import unittest
import numpy as np
from nose.tools                import raises
from filterpy.kalman           import KalmanFilter,ExtendedKalmanFilter
from fdia_simulation.models    import Radar, PeriodRadar
from fdia_simulation.attackers import Attacker, DOSAttacker, DriftAttacker, CumulativeDriftAttacker

class AttackerTestCase(unittest.TestCase):
    def setUp(self):
        # Simulated filter for 2 radars (2*3 measurements)
        self.filter = ExtendedKalmanFilter(dim_x = 9, dim_z = 6)
        # Attack matrix: second radar is compromised
        self.gamma  = np.array([[0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 1, 0, 0],
                                [0, 0, 0, 0, 1, 0],
                                [0, 0, 0, 0, 0, 1]])

        self.mag_vector = np.array([[0, 0, 0, -10, -10, -10]]).T
        self.t0 = 10
        self.time = 50
        self.radar = Radar(x=10,y=10)
        self.attacker = Attacker(filter = self.filter, radar = self.radar,
                                      gamma = self.gamma,mag_vector = self.mag_vector,
                                      t0 = self.t0, time = self.time)

    # ==========================================================================
    # ========================== Initialization tests ==========================

    def test_initialization_no_errors(self):
        self.assertTrue(np.array_equal(self.attacker.gamma,self.gamma))
        self.assertTrue(np.array_equal(self.attacker.mag_vector,self.mag_vector))
        self.assertEqual(self.t0,10)
        self.assertEqual(self.time,50)

    def test_initialization_wrong_mag_vector(self):
        with self.assertRaises(ValueError):
            mag_vector = np.array([[0,0,0,-10]])
            att  = Attacker(filter = self.filter, radar = self.radar,
                                 gamma = self.gamma,mag_vector = mag_vector,
                                 t0 = self.t0, time = self.time)

    def test_initialization_wrong_gamma(self):
        with self.assertRaises(ValueError):
            filter = ExtendedKalmanFilter(dim_x = 9, dim_z = 6)
            gamma  = np.array([[0, 0, 0, 0],
                               [0, 0, 0, 0],
                               [0, 0, 0, 0],
                               [0, 0, 0, 1]])
            att  =  Attacker(filter = self.filter, radar = self.radar,
                                  gamma = gamma, mag_vector = self.mag_vector,
                                  t0 = self.t0, time = self.time)

    def test_initialization_attack_no_effect(self):
        with self.assertWarns(Warning):
            mag_vector = np.array([[10, 100, 50, 0, 0, 0]]).T
            att  =  Attacker(filter = self.filter, radar = self.radar,
                                          gamma = self.gamma, mag_vector = mag_vector,
                                          t0 = self.t0, time = self.time)

    def test_initialization_radar_position_0(self):
        # Expected results
        gamma =  np.array([[1, 0, 0, 0, 0, 0],
                           [0, 1, 0, 0, 0, 0],
                           [0, 0, 1, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0]])
        mag_vector = np.array([[1,1,1,0,0,0]]).T
        radar_pos = 0

        #Generation
        att = Attacker(filter = self.filter, radar_pos = radar_pos,
                            radar = self.radar,t0 = self.t0, time = self.time)
        computed_gamma      = att.gamma
        computed_mag_vector = att.mag_vector

        # Comparison
        self.assertTrue(np.array_equal(gamma,computed_gamma))
        self.assertTrue(np.array_equal(mag_vector,computed_mag_vector))


    def test_initialization_radar_position_1(self):
        # Expected results
        gamma =  np.array([[0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 1, 0, 0],
                           [0, 0, 0, 0, 1, 0],
                           [0, 0, 0, 0, 0, 1]])
        mag_vector = np.array([[0,0,0,1,1,1]]).T
        radar_pos = 1

        #Generation
        att = Attacker(filter = self.filter, radar_pos = radar_pos,
                            radar = self.radar, t0 = self.t0, time = self.time)
        computed_gamma      = att.gamma
        computed_mag_vector = att.mag_vector

        # Comparison
        self.assertTrue(np.array_equal(gamma,computed_gamma))
        self.assertTrue(np.array_equal(mag_vector,computed_mag_vector))


    # ==========================================================================
    # ========================== Listening/Attack tests ========================

    def test_listen_measurement_increments_time(self):
        measurements = [np.ones((6,1))*i for i in range(100)]
        for i,measurement in enumerate(measurements):
            self.assertEqual(self.attacker.current_time,i)
            self.attacker.listen_measurement(measurement)

    def test_listen_measurement_1_step_attack(self):
        measurement          = np.array([[10,10,10,10,10,10]]).T
        modified_measurement = np.array([[10,10,10,0,0,0]]).T

        self.attacker.t0     = 0
        computed_measurement = self.attacker.listen_measurement(measurement)
        self.assertTrue(np.array_equal(modified_measurement,computed_measurement))

    def test_listen_measurement_1_step_no_attack(self):
        measurement          = np.array([[1,1,1,1,1,1]]).T
        computed_measurement = self.attacker.listen_measurement(measurement)
        self.assertTrue(np.array_equal(measurement,computed_measurement))

    def test_unattacked_vectors(self):
        measurements = [np.ones((6,1))*i for i in range(100)]
        modified_measurements = []
        for i,measurement in enumerate(measurements):
            mod_meas = self.attacker.listen_measurement(measurement)
            modified_measurements.append(mod_meas)

        # Unattacked measurements are the ones from 0:10 and 60:100
        unattacked_meas_1 = [np.ones((6,1))*i for i in range(0,10)  ]
        unattacked_meas_2 = [np.ones((6,1))*i for i in range(60,100)]

        comparison_list_1 = zip(unattacked_meas_1,  modified_measurements[0:10])
        comparison_list_2 = zip(unattacked_meas_2,  modified_measurements[60:100])
        self.assertTrue(all([np.allclose(meas, mod_meas) for meas, mod_meas in comparison_list_1]))
        self.assertTrue(all([np.allclose(meas, mod_meas) for meas, mod_meas in comparison_list_2]))

    def test_attacked_vectors(self):
        measurements =[np.ones((6,1))*i for i in range(100)]
        modified_measurements = []
        for i,measurement in enumerate(measurements):
            mod_meas = self.attacker.listen_measurement(measurement)
            modified_measurements.append(mod_meas)

        attacked_meas = [np.subtract(np.array([[i,i,i,i,i,i]]).T,np.array([[0,0,0,10,10,10]]).T) for i in range(10,60)]
        comparison_list = zip(attacked_meas,  modified_measurements[10:60])
        self.assertTrue(all([np.allclose(meas, mod_meas) for meas, mod_meas in comparison_list]))

class DOSAttackerTestCase(AttackerTestCase):
    def setUp(self):
        AttackerTestCase.setUp(self)
        self.mag = 1e6
        self.attacker = DOSAttacker(filter = self.filter, mag = self.mag,
                                           gamma = self.gamma,mag_vector = self.mag_vector,
                                           radar = self.radar, t0 = self.t0, time = self.time)

    def test_initialization_no_errors(self):
        self.assertTrue(np.array_equal(self.attacker.gamma,self.gamma))
        self.assertEqual(self.t0,10)
        self.assertEqual(self.time,50)

    def test_listen_measurement_1_step_attack(self):
        measurement          = np.array([[10,10,10,10,10,10]]).T
        modified_measurement = np.array([[10,10,10,-9.99999e6,-9.99999e6,-9.99999e6]]).T
        self.attacker.t0     = 0
        computed_measurement = self.attacker.listen_measurement(measurement)
        self.assertTrue(np.array_equal(modified_measurement,computed_measurement))

    def test_attacked_vectors(self):
        pass

class DriftAttackerTestCase(AttackerTestCase):
    def setUp(self):
        self.radar_position = 1
        AttackerTestCase.setUp(self)
        self.attacker = DriftAttacker(filter = self.filter,
                                      radar = self.radar, radar_pos = self.radar_position,
                                      t0 = self.t0, time = self.time)

    def test_initialization_no_errors(self):
        self.assertTrue(np.array_equal(self.attacker.gamma,self.gamma))
        self.assertEqual(self.t0,10)
        self.assertEqual(self.time,50)
        self.assertEqual(self.radar, Radar(x=10,y=10))
        self.assertTrue(np.array_equal(self.attacker.attack_drift,np.array([[0,0,10]]).T))

    def test_listen_measurement_1_step_attack(self):
        measurement          = np.array([[10,10,10,10,10,10]]).T
        modified_measurement = np.array([[10.,10.,10.,9.,0.,0.]]).T
        self.attacker.t0     = 0
        computed_measurement = self.attacker.listen_measurement(measurement)
        print(computed_measurement)
        self.assertTrue(np.allclose(modified_measurement,computed_measurement))

    def test_attacked_vectors(self):
        pass


class CumulativeDriftAttackerTestCase(AttackerTestCase):
    def setUp(self):
        self.radar_position = 1
        self.delta_drift = np.array([[0,0,1]]).T
        AttackerTestCase.setUp(self)
        self.attacker = CumulativeDriftAttacker(filter = self.filter,
                                                radar = self.radar, radar_pos = self.radar_position,
                                                delta_drift = self.delta_drift,
                                                t0 = self.t0, time = self.time)

    def test_initialization_no_errors(self):
        self.assertTrue(np.array_equal(self.attacker.gamma,self.gamma))
        self.assertEqual(self.t0,10)
        self.assertEqual(self.time,50)
        self.assertEqual(self.radar, Radar(x=10,y=10))
        self.assertTrue(np.array_equal(self.attacker.delta_drift,np.array([[0,0,1]]).T))
        self.assertTrue(np.array_equal(self.attacker.attack_drift,np.array([[0,0,1]]).T))

    def test_listen_measurement_1_step_attack(self):
        measurement          = np.array([[10,10,10,10,10,10]]).T
        modified_measurement = np.array([[10.,10.,10.,9.,0.,0.]]).T
        self.attacker.t0     = 0
        computed_measurement = self.attacker.listen_measurement(measurement)
        print(computed_measurement)
        print(self.attacker)
        self.assertTrue(np.allclose(modified_measurement,computed_measurement))

    def test_attacked_vectors(self):
        pass



if __name__ == "__main__":
    unittest.main()
