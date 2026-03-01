"""Tests for starwars module constants and play_starwars function."""

import unittest
from unittest.mock import MagicMock, patch

from create_serial.starwars import (
    play_starwars,
    a4, c4, c5, e5, f4, g5,
    MEASURE, HALF, Q, E, Ed, S,
    MEASURE_TIME,
)


class TestNoteConstants(unittest.TestCase):
    def test_midi_note_values(self):
        self.assertEqual(c4, 60)
        self.assertEqual(a4, 69)
        self.assertEqual(c5, 72)
        self.assertEqual(e5, 76)
        self.assertEqual(f4, 65)
        self.assertEqual(g5, 79)

    def test_note_range(self):
        # All notes should be valid MIDI (31-127 for Roomba)
        self.assertGreaterEqual(c4, 31)
        self.assertLessEqual(c5, 127)


class TestDurations(unittest.TestCase):
    def test_measure_is_160(self):
        self.assertEqual(MEASURE, 160)

    def test_half(self):
        self.assertEqual(HALF, MEASURE // 2)

    def test_quarter(self):
        self.assertEqual(Q, MEASURE // 4)

    def test_eighth(self):
        self.assertEqual(E, MEASURE // 8)

    def test_dotted_eighth(self):
        self.assertEqual(Ed, MEASURE * 3 // 16)

    def test_sixteenth(self):
        self.assertEqual(S, MEASURE // 16)

    def test_measure_time(self):
        self.assertAlmostEqual(MEASURE_TIME, MEASURE / 64.0)

    def test_durations_fit_in_byte(self):
        # All durations should be 0-255 (one byte)
        for dur in [HALF, Q, E, Ed, S]:
            self.assertGreaterEqual(dur, 0)
            self.assertLessEqual(dur, 255)


class TestPlayStarwars(unittest.TestCase):
    @patch('create_serial.starwars.time.sleep')
    def test_play_starwars_calls_set_song(self, mock_sleep):
        mock_robot = MagicMock()
        play_starwars(mock_robot)

        # Should call setSong multiple times
        self.assertTrue(mock_robot.setSong.called)
        self.assertGreaterEqual(mock_robot.setSong.call_count, 3)

        # Should call playSongNumber multiple times
        self.assertTrue(mock_robot.playSongNumber.called)
        self.assertGreaterEqual(mock_robot.playSongNumber.call_count, 6)

    @patch('create_serial.starwars.time.sleep')
    def test_play_starwars_song_data_valid(self, mock_sleep):
        mock_robot = MagicMock()
        play_starwars(mock_robot)

        # Check that all song data contains valid (note, duration) tuples
        for call_obj in mock_robot.setSong.call_args_list:
            song_num, song_data = call_obj[0]
            self.assertGreaterEqual(song_num, 0)
            self.assertLessEqual(song_num, 15)
            self.assertLessEqual(len(song_data), 16)
            for note, duration in song_data:
                self.assertGreaterEqual(note, 0)
                self.assertLessEqual(note, 127)
                self.assertGreaterEqual(duration, 0)
                self.assertLessEqual(duration, 255)


if __name__ == '__main__':
    unittest.main()
