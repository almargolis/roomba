# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python 3 port of [martinschaef/roomba](https://github.com/martinschaef/roomba) — a library for controlling iRobot Roomba via the serial Open Interface (OI) protocol over USB cable. Published on PyPI as `create-serial` (import as `create_serial`). Tested with Roomba 770 and compatible with Create 2.

## Running

```bash
# Set up virtual environment
python -m venv venv && source venv/bin/activate
pip install -e ".[game]"

# Or install dependencies directly
pip install pyserial pygame-ce

# Run tests
python -m pytest tests/ -v

# Pygame controller (drive with w/a/s/d, live sensor display)
roomba-game [/dev/ttyUSB0]

# Play Star Wars Imperial March through Roomba speaker
roomba-starwars [/dev/ttyUSB0]
```

Port auto-detects by scanning `/dev/tty.usbserial-*` (macOS) and `/dev/ttyUSB*` (Linux). On Linux, the user must be in the `dialout` group.

## Architecture

The package uses a `src/` layout:

```
src/create_serial/
├── __init__.py    # Re-exports public API from create module
├── create.py      # Core library
├── game.py        # Pygame GUI controller
└── starwars.py    # Star Wars music player
tests/
├── test_utils.py
├── test_sensor_frame.py
├── test_create.py
├── test_find_port.py
└── test_starwars.py
```

- **`create.py`** — Core library. The `Create` class wraps pyserial to send OI protocol commands (opcode bytes) and parse sensor responses. Module-level constants define opcodes (START, DRIVE, SENSORS, etc.) and sensor IDs (BUMPS_AND_WHEEL_DROPS, WALL_SIGNAL, etc.). `SensorFrame` is a data struct for sensor snapshots. Helper functions handle two's-complement byte encoding. `find_port()` does serial port auto-detection.

- **`game.py`** — Pygame GUI that instantiates `Create`, polls sensors in a game loop, and renders a top-down Roomba diagram with live sensor values. Keyboard input maps to `robot.go_differential()` and `robot.motors()` calls. Entry point: `main()`.

- **`starwars.py`** — Defines MIDI notes and durations, uploads song chunks via `robot.setSong()`, and plays them sequentially with timed `time.sleep()` gaps. Entry point: `main()`.

## Serial Protocol Patterns

All OI commands are sent as raw bytes via `self._write(bytes([opcode]))`. When modifying or adding commands:
- Use `bytes([x])` for single-byte values (not `chr(x)` — this was a Python 2 pattern)
- Multi-byte values use `_toTwosComplement2Bytes()` for signed ints
- Serial reads return `bytes` objects; iterate directly for int values (no `ord()` needed)
- Compare empty reads against `b''`, not `''`
- Use `//` for integer division (e.g., note durations in starwars.py)

## Units Convention

All angles in the public API use **radians** (standard engineering practice):
- `go_differential(cm_per_sec, rad_per_sec)` — drive command (renamed from `go()`)
- `turn(angle_rad, rad_per_sec)` — scripted turn
- `getPose(dist='cm')` — returns `(x, y, th_radians)`
- `setPose(x, y, th_radians, dist='cm')` — sets internal odometry

Degrees are only used at the OI protocol boundary (e.g., `_waitForAngle` converts radians to degrees for the WAITANGLE opcode).

## Odometry Calibration

Encoder-based odometry drifts over time (this is inherent to differential-drive robots). If rotation is consistently off, adjust `WHEEL_SPAN` in `create.py` — the default 235mm matches the Create 2 spec but varies with floor surface and tire wear.
