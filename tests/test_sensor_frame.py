"""Tests for SensorFrame class."""

import unittest

from create_serial.create import SensorFrame


class TestSensorFrameInit(unittest.TestCase):
    def test_defaults_are_zero(self):
        sf = SensorFrame()
        self.assertEqual(sf.leftBump, 0)
        self.assertEqual(sf.rightBump, 0)
        self.assertEqual(sf.wallSensor, 0)
        self.assertEqual(sf.distance, 0)
        self.assertEqual(sf.rawAngle, 0)
        self.assertEqual(sf.angleInRadians, 0)
        self.assertEqual(sf.voltage, 0)
        self.assertEqual(sf.current, 0)
        self.assertEqual(sf.charge, 0)
        self.assertEqual(sf.capacity, 0)
        self.assertEqual(sf.lightBumpLeft, 0)
        self.assertEqual(sf.dirt, 0)

    def test_str_contains_fields(self):
        sf = SensorFrame()
        s = str(sf)
        self.assertIn('leftBump:', s)
        self.assertIn('rightBump:', s)
        self.assertIn('wallSensor:', s)
        self.assertIn('distance:', s)
        self.assertIn('angleInRadians:', s)
        self.assertIn('angleInDegrees:', s)
        self.assertIn('voltage:', s)
        self.assertIn('charge:', s)
        self.assertIn('capacity:', s)

    def test_str_with_nonzero_values(self):
        sf = SensorFrame()
        sf.voltage = 15000
        sf.leftBump = 1
        s = str(sf)
        self.assertIn('15000', s)
        self.assertIn('leftBump: 1', s)

    def test_to_binary_string_length(self):
        sf = SensorFrame()
        result = sf._toBinaryString()
        self.assertEqual(len(result), 26)
        self.assertIsInstance(result, bytes)

    def test_to_binary_string_roundtrip_distance(self):
        sf = SensorFrame()
        sf.distance = 100
        result = sf._toBinaryString()
        # bytes 12, 13 should encode 100
        self.assertEqual(result[12], 0)
        self.assertEqual(result[13], 100)


if __name__ == '__main__':
    unittest.main()
