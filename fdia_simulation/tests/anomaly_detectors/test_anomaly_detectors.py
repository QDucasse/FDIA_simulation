# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 14:28:45 2019

@author: qde
"""

import unittest
from nose.tools                      import raises
from numpy.random                    import randn
from filterpy.common                 import kinematic_kf
from fdia_simulation.anomaly_detectors import MahalanobisDetector, EuclidianDetector, AnomalyDetector



class AnomalyDetectorTestCase(unittest.TestCase):
    @raises(TypeError)
    def test_no_initialization(self):
        abstractClassInstance = AnomalyDetector()

class MahalanobisDetectorTestCase(unittest.TestCase):
    def setUp(self):
        self.kinematic_test_kf = kinematic_kf(dim=1,order=1,dt=1)
        x         = [0.,2.]
        self.zs   = [x[0]]
        self.pos  = [x[0]]
        noise_std = 1.

        # Noisy measurements generation for 30 samples
        for _ in range(30):
            last_pos = x[0]
            last_vel = x[1]
            new_vel  = last_vel
            new_pos  = last_pos + last_vel
            x = [new_pos, new_vel]
            z = new_pos + (randn()*noise_std)
            self.zs.append(z)

        # Outlier generation
        self.zs[5]  += 10.
        self.zs[10] += 10.
        self.zs[15] += 10.
        self.zs[20] += 10.
        self.zs[25] += 10.

        self.detector = MahalanobisDetector()

    def test_initial_reviewed_values(self):
        self.assertEqual(self.detector.reviewed_values,[])

    def test_correct_value_not_detected(self):
        self.kinematic_test_kf.predict()
        result = self.detector.review_measurement(self.zs[0],self.kinematic_test_kf)
        self.assertEqual(result,True)

    def test_correct_value_added_to_reviewed_list(self):
        self.kinematic_test_kf.predict()
        self.assertEqual(0, len(self.detector.reviewed_values))
        self.detector.review_measurement(self.zs[0],self.kinematic_test_kf)
        self.assertEqual(1, len(self.detector.reviewed_values))

    def test_probabilities_added_to_reviewed_list(self):
        for z in self.zs:
            self.kinematic_test_kf.predict()
            self.detector.review_measurement(z,self.kinematic_test_kf)
            self.kinematic_test_kf.update(z)
        self.assertEqual(31,len(self.detector.reviewed_values))

    def test_wrong_value_detected(self):
        # First correct values
        for i in range(6):
            self.kinematic_test_kf.predict()
            self.detector.review_measurement(self.zs[i],self.kinematic_test_kf)
            self.kinematic_test_kf.update(self.zs[i])
        # Incorrect value
        self.kinematic_test_kf.predict()
        result = self.detector.review_measurement(self.zs[6],self.kinematic_test_kf)
        self.kinematic_test_kf.update(self.zs[6])
        self.assertEqual(result,False)


class EuclidianDetectorTestCase(MahalanobisDetectorTestCase):
    def setUp(self):
        MahalanobisDetectorTestCase.setUp(self)
        self.detector = EuclidianDetector()
        
if __name__ == "__main__":
    unittest.main()
