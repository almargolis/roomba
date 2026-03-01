"""Tests for Create class with mocked serial port."""

import unittest
from unittest.mock import MagicMock, patch, call

from create_serial.create import (
    Create,
    modeStr,
    OFF_MODE,
    PASSIVE_MODE,
    SAFE_MODE,
    FULL_MODE,
    START,
    SAFE,
    DRIVE,
    MOTORS,
    LEDS,
    SONG,
    PLAY,
    SENSORS,
    QUERYLIST,
    ENCODER_LEFT,
    ENCODER_RIGHT,
    DISTANCE,
    ANGLE,
    SENSOR_DATA_WIDTH,
    _toTwosComplement2Bytes,
)


def make_robot():
    """Create a Create instance with a fully mocked serial port."""
    with patch('create_serial.create.serial.Serial') as MockSerial:
        mock_ser = MagicMock()
        mock_ser.isOpen.return_value = True
        # sensors() during __init__ calls _getRawSensorDataAsList which
        # does ser.read; return empty data for initial sensor reads
        mock_ser.read.return_value = b''
        MockSerial.return_value = mock_ser
        robot = Create(PORT='/dev/fake', startingMode=SAFE_MODE)
    return robot


class TestCreateConstructor(unittest.TestCase):
    def test_creates_with_mock_serial(self):
        robot = make_robot()
        self.assertIsNotNone(robot)
        self.assertEqual(robot.sciMode, SAFE_MODE)

    def test_initial_pose_is_zero(self):
        robot = make_robot()
        x, y, th = robot.getPose()
        self.assertEqual(x, 0.0)
        self.assertEqual(y, 0.0)
        self.assertEqual(th, 0.0)


class TestGo(unittest.TestCase):
    def test_go_zero(self):
        robot = make_robot()
        robot.ser.write.reset_mock()
        robot.go(0, 0)
        # Should send DRIVE command with velocity 0 and direction CCW (radius=1)
        calls = robot.ser.write.call_args_list
        self.assertTrue(len(calls) > 0)

    def test_stop(self):
        robot = make_robot()
        robot.ser.write.reset_mock()
        robot.ser.read.return_value = b'\x00' * 4  # DISTANCE + ANGLE = 4 bytes
        robot.stop()
        # stop() calls go(0,0) then sensors([POSE])
        calls = robot.ser.write.call_args_list
        self.assertTrue(len(calls) > 0)


class TestMotors(unittest.TestCase):
    def test_motors_all_off(self):
        robot = make_robot()
        robot.ser.write.reset_mock()
        robot.motors(0, 0, 0)
        calls = robot.ser.write.call_args_list
        # Should write MOTORS opcode then a byte
        self.assertEqual(calls[0], call(MOTORS))
        self.assertEqual(calls[1], call(bytes([0])))

    def test_motors_all_on(self):
        robot = make_robot()
        robot.ser.write.reset_mock()
        robot.motors(1, 1, 1)
        calls = robot.ser.write.call_args_list
        self.assertEqual(calls[0], call(MOTORS))
        # side_brush=1 -> bit0=1, main_brush=1 -> bit2=1, vacuum=1 -> bit1=1
        # = 0b00000111 = 7
        self.assertEqual(calls[1], call(bytes([7])))


class TestSetLEDs(unittest.TestCase):
    def test_set_leds(self):
        robot = make_robot()
        robot.ser.write.reset_mock()
        robot.setLEDs(128, 255, 0, 1)
        calls = robot.ser.write.call_args_list
        self.assertEqual(calls[0], call(LEDS))
        # advance=1 -> bit3, play=0 -> firstByteVal = 8
        self.assertEqual(calls[1], call(bytes([8])))
        # power_color=128
        self.assertEqual(calls[2], call(bytes([128])))
        # power_intensity=255
        self.assertEqual(calls[3], call(bytes([255])))


class TestSetSong(unittest.TestCase):
    def test_set_song(self):
        robot = make_robot()
        robot.ser.write.reset_mock()
        robot.setSong(1, [(60, 32), (64, 32)])
        calls = robot.ser.write.call_args_list
        self.assertEqual(calls[0], call(SONG))
        self.assertEqual(calls[1], call(bytes([1])))   # song number
        self.assertEqual(calls[2], call(bytes([2])))   # length
        self.assertEqual(calls[3], call(bytes([60])))  # note 1
        self.assertEqual(calls[4], call(bytes([32])))  # duration 1
        self.assertEqual(calls[5], call(bytes([64])))  # note 2
        self.assertEqual(calls[6], call(bytes([32])))  # duration 2

    def test_set_song_empty_list(self):
        robot = make_robot()
        robot.ser.write.reset_mock()
        robot.setSong(0, [])
        # Should return without writing anything
        calls = robot.ser.write.call_args_list
        self.assertEqual(len(calls), 0)

    def test_set_song_clamps_number(self):
        robot = make_robot()
        robot.ser.write.reset_mock()
        robot.setSong(20, [(60, 32)])  # 20 > 15, should clamp to 15
        calls = robot.ser.write.call_args_list
        self.assertEqual(calls[1], call(bytes([15])))


class TestPose(unittest.TestCase):
    def test_get_set_pose_cm_deg(self):
        robot = make_robot()
        robot.setPose(10, 20, 90, dist='cm', angle='deg')
        x, y, th = robot.getPose(dist='cm', angle='deg')
        self.assertAlmostEqual(x, 10.0)
        self.assertAlmostEqual(y, 20.0)
        self.assertAlmostEqual(th, 90.0, places=1)

    def test_reset_pose(self):
        robot = make_robot()
        robot.setPose(10, 20, 90)
        robot.resetPose()
        x, y, th = robot.getPose()
        self.assertEqual(x, 0.0)
        self.assertEqual(y, 0.0)
        self.assertEqual(th, 0.0)

    def test_get_pose_mm_rad(self):
        robot = make_robot()
        robot.setPose(100, 200, 1.5, dist='mm', angle='rad')
        x, y, th = robot.getPose(dist='mm', angle='rad')
        self.assertAlmostEqual(x, 100.0)
        self.assertAlmostEqual(y, 200.0)
        self.assertAlmostEqual(th, 1.5)


class TestModeStr(unittest.TestCase):
    def test_all_modes(self):
        self.assertEqual(modeStr(OFF_MODE), 'OFF_MODE')
        self.assertEqual(modeStr(PASSIVE_MODE), 'PASSIVE_MODE')
        self.assertEqual(modeStr(SAFE_MODE), 'SAFE_MODE')
        self.assertEqual(modeStr(FULL_MODE), 'FULL_MODE')

    def test_unknown_mode(self):
        result = modeStr(99)
        self.assertEqual(result, 'UNKNOWN_MODE')


if __name__ == '__main__':
    unittest.main()
