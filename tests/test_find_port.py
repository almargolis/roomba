"""Tests for find_port() with mocked glob."""

import unittest
from unittest.mock import patch

from create_serial.create import find_port


class TestFindPort(unittest.TestCase):
    @patch('create_serial.create.glob.glob')
    def test_single_port_found(self, mock_glob):
        mock_glob.side_effect = lambda pat: (
            ['/dev/tty.usbserial-AB1234'] if 'usbserial' in pat else []
        )
        result = find_port()
        self.assertEqual(result, '/dev/tty.usbserial-AB1234')

    @patch('create_serial.create.glob.glob')
    def test_single_linux_port(self, mock_glob):
        mock_glob.side_effect = lambda pat: (
            ['/dev/ttyUSB0'] if 'ttyUSB' in pat else []
        )
        result = find_port()
        self.assertEqual(result, '/dev/ttyUSB0')

    @patch('create_serial.create.glob.glob')
    def test_no_ports_exits(self, mock_glob):
        mock_glob.return_value = []
        with self.assertRaises(SystemExit):
            find_port()

    @patch('create_serial.create.glob.glob')
    def test_multiple_ports_exits(self, mock_glob):
        mock_glob.side_effect = lambda pat: (
            ['/dev/tty.usbserial-A', '/dev/tty.usbserial-B'] if 'usbserial' in pat else []
        )
        with self.assertRaises(SystemExit):
            find_port()


if __name__ == '__main__':
    unittest.main()
