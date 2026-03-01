"""Tests for byte manipulation helper functions in create_serial.create."""

import unittest

from create_serial.create import (
    _bitOfByte,
    _toTwosComplement2Bytes,
    _twosComplementInt1byte,
    _twosComplementInt2bytes,
)


class TestBitOfByte(unittest.TestCase):
    def test_bit0(self):
        self.assertEqual(_bitOfByte(0, 0b00000001), 1)
        self.assertEqual(_bitOfByte(0, 0b11111110), 0)

    def test_bit7(self):
        self.assertEqual(_bitOfByte(7, 0b10000000), 1)
        self.assertEqual(_bitOfByte(7, 0b01111111), 0)

    def test_middle_bits(self):
        self.assertEqual(_bitOfByte(3, 0b00001000), 1)
        self.assertEqual(_bitOfByte(3, 0b11110111), 0)

    def test_out_of_range(self):
        self.assertEqual(_bitOfByte(-1, 0xFF), 0)
        self.assertEqual(_bitOfByte(8, 0xFF), 0)


class TestTwosComplementInt1Byte(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(_twosComplementInt1byte(0), 0)

    def test_positive(self):
        self.assertEqual(_twosComplementInt1byte(1), 1)
        self.assertEqual(_twosComplementInt1byte(127), 127)

    def test_negative(self):
        self.assertEqual(_twosComplementInt1byte(0xFF), -1)
        self.assertEqual(_twosComplementInt1byte(0x80), -128)
        self.assertEqual(_twosComplementInt1byte(0xFE), -2)


class TestTwosComplementInt2Bytes(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(_twosComplementInt2bytes(0, 0), 0)

    def test_positive(self):
        self.assertEqual(_twosComplementInt2bytes(0, 1), 1)
        self.assertEqual(_twosComplementInt2bytes(0x01, 0x00), 256)
        self.assertEqual(_twosComplementInt2bytes(0x7F, 0xFF), 32767)

    def test_negative(self):
        self.assertEqual(_twosComplementInt2bytes(0xFF, 0xFF), -1)
        self.assertEqual(_twosComplementInt2bytes(0x80, 0x00), -32768)
        self.assertEqual(_twosComplementInt2bytes(0xFF, 0xFE), -2)


class TestToTwosComplement2Bytes(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(_toTwosComplement2Bytes(0), (0, 0))

    def test_positive(self):
        self.assertEqual(_toTwosComplement2Bytes(1), (0, 1))
        self.assertEqual(_toTwosComplement2Bytes(256), (1, 0))
        self.assertEqual(_toTwosComplement2Bytes(500), (1, 244))

    def test_negative(self):
        high, low = _toTwosComplement2Bytes(-1)
        self.assertEqual((high, low), (0xFF, 0xFF))

        high, low = _toTwosComplement2Bytes(-500)
        # verify round-trip
        self.assertEqual(_twosComplementInt2bytes(high, low), -500)

    def test_roundtrip(self):
        for val in [0, 1, -1, 100, -100, 500, -500, 32767, -32768]:
            high, low = _toTwosComplement2Bytes(val)
            self.assertEqual(_twosComplementInt2bytes(high, low), val)


if __name__ == '__main__':
    unittest.main()
