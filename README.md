# create-serial

Python 3 library for controlling iRobot Roomba/Create via the serial Open Interface (OI) protocol over USB cable. This work is based on the script from [this](http://web.archive.org/web/20160827153405/http://cs.gmu.edu/~zduric/cs101/pmwiki.php/Main/APITutorial) course. I adjusted it a bit to get access to the light bump in the Create 2 and my Roomba 770.

Ported to Python 3 from the original Python 2.7 code by [Martin Schaef](https://github.com/martinschaef/roomba).

### Installation

    pip install create-serial

To include pygame for the game controller:

    pip install create-serial[game]

### Files

- **`src/create_serial/create.py`** — Library module. Provides the `Create` class that handles all serial communication with the Roomba. Not run directly.
- **`src/create_serial/game.py`** — Pygame-based controller. Opens a window to drive the Roomba with w/a/s/d and displays live sensor data.
- **`src/create_serial/cli.py`** — Terminal-based controller. Works over SSH without a display server.
- **`src/create_serial/starwars.py`** — Plays the Star Wars Imperial March through the Roomba's speaker.

### Dependencies

    pip install pyserial pygame-ce

(`pygame-ce` is the community edition of pygame, required for Python 3.14+ support.)

### Running

All commands auto-detect the serial port. Just plug in the USB cable and run:

    roomba-game
    roomba-cli
    roomba-starwars

To specify a port explicitly, pass it as an argument:

    roomba-game /dev/ttyUSB0
    roomba-cli /dev/tty.usbserial-XXXXXXXX
    roomba-starwars /dev/tty.usbserial-XXXXXXXX

You can also run as modules from a development checkout:

    python -m create_serial.game [/dev/ttyUSB0]
    python -m create_serial.cli [/dev/ttyUSB0]
    python -m create_serial.starwars [/dev/ttyUSB0]

If no port is given, the scripts scan `/dev/` for `tty.usbserial-*` (macOS) and `ttyUSB*` (Linux/RPi). If zero or multiple ports are found, an error message is printed with instructions.

### Game controls

- **w/a/s/d** — Drive forward/left/back/right
- **Up/Down** — Adjust speed
- **m** — Main brush (Shift+m to reverse)
- **o** — Side brush (Shift+o to reverse)
- **v** — Vacuum
- **Space** — Reset position estimate
- **Esc** — Quit

### Use as library

    from create_serial import Create, WALL_SIGNAL
    import math, time

    robot = Create()              # auto-detect port
    robot = Create('/dev/ttyUSB0') # or specify port
    robot.printSensors()
    wall_fun = robot.senseFunc(WALL_SIGNAL)
    print(wall_fun())
    robot.toSafeMode()
    robot.go_differential(0, 1.75)  # spin at ~1.75 rad/sec
    time.sleep(2.0)
    robot.go_differential(10, 0)    # drive forward at 10 cm/sec
    time.sleep(2.0)
    robot.stop()
    robot.close()

### API reference

All angles use **radians**. Distances use centimeters by default.

#### Driving

- **`go_differential(cm_per_sec=0, rad_per_sec=0)`** — Set translational and rotational velocity. Positive `rad_per_sec` turns left (CCW).
- **`stop()`** — Stop all movement (equivalent to `go_differential(0, 0)`).
- **`setWheelVelocities(left_cm_sec, right_cm_sec)`** — Set each wheel independently (capped at ±50 cm/sec).

#### Scripted moves

- **`move(distance_cm, cm_per_sec=10)`** — Drive a fixed distance. Blocks until complete.
- **`turn(angle_rad, rad_per_sec=0.35)`** — Rotate a fixed angle. Blocks until complete.

#### Odometry

- **`getPose(dist='cm')`** — Returns `(x, y, th)` where `th` is in radians. Use `dist='mm'` for millimeters.
- **`setPose(x, y, th, dist='cm')`** — Set the internal odometry estimate. `th` is in radians.
- **`resetPose()`** — Reset odometry to `(0, 0, 0)`.

#### Sensors

- **`sensors(list_of_sensors)`** — Poll sensors. Pass a list of sensor IDs (e.g. `[WALL_SIGNAL, LEFT_BUMP]`) or a frame number (0–6). Returns a dict.
- **`printSensors()`** — Poll and print all sensor values.
- **`senseFunc(sensor_id)`** — Returns a callable that polls and returns a single sensor value.

#### Peripherals

- **`motors(side_brush=0, main_brush=0, vacuum=0)`** — Control cleaning motors. Values: -1 (reverse), 0 (off), 1 (forward).
- **`setLEDs(power_color, power_intensity, play, advance)`** — Set LEDs. Power color/intensity 0–255, play/advance 0 or 1.
- **`setSong(songNumber, songDataList)`** — Store a song (0–15). Data is list of `(midi_note, duration)` tuples.
- **`playSong(list_of_notes)`** — Store and play a song immediately.
- **`playNote(noteNumber, duration)`** — Play a single MIDI note.

#### Mode control

- **`toSafeMode()`** — Enter safe mode (stops on cliff/wheel drop).
- **`toFullMode()`** — Enter full mode (no safety cutoffs).
- **`close()`** — Return to passive mode and close the serial port.

For more information read the original [tutorial](http://web.archive.org/web/20160827153405/http://cs.gmu.edu/~zduric/cs101/pmwiki.php/Main/APITutorial). The list of all available sensors is [here](https://github.com/martinschaef/roomba/blob/master/create.py#L70).

### Setup

Tested with a Roomba 770 using the iRobot [serial cable](http://store.irobot.com/communication-cable-create-2/product.jsp?productId=54235746) on macOS and Raspberry Pi.

**Serial port names by platform:**
- **macOS:** `/dev/tty.usbserial-XXXXXXXX`
- **Raspberry Pi / Linux / Ubuntu:** `/dev/ttyUSB0`

**Linux permissions:** On Ubuntu and other Linux distros, you need to be in the `dialout` group to access serial ports:

    sudo usermod -aG dialout $USER

Log out and back in (or reboot) for this to take effect. Without this you'll get `Permission denied` when connecting.

If the Roomba does not connect properly, check the cable first, then check if the port is correct, and then check if the baud rate in create.py is correct.

### Odometry calibration

Encoder-based odometry will always drift over time, but it should be reasonable for short distances. If rotation angles are consistently off, adjust the `WHEEL_SPAN` constant in `create.py` — increase it if the robot over-rotates, decrease it if it under-rotates. The default of 235mm matches the Create 2 spec but the effective wheelbase varies with floor surface and tire wear.
