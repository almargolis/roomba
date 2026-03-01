#
# cli.py
#
# Terminal-based controller for the Roomba.
# Works over SSH — no display server required.
#
# Usage: roomba-cli [port]
#   port is optional - auto-detects if not provided.
# Control the Roomba with keyboard keys.
# Only stdlib modules are used (no curses, no pygame).
import select
import sys
import termios
import time
import tty

from . import create


MAX_FORWARD = 50   # cm per second
MAX_ROTATION = 200 # degrees per second
SPEED_INC = 10     # increment in percent

SENSOR_NAMES = {
    create.LEFT_BUMP: "Left Bump",
    create.RIGHT_BUMP: "Right Bump",
    create.WALL_IR_SENSOR: "Wall IR",
    create.WALL_SIGNAL: "Wall Signal",
    create.CLIFF_LEFT_SIGNAL: "Cliff L",
    create.CLIFF_FRONT_LEFT_SIGNAL: "Cliff FL",
    create.CLIFF_FRONT_RIGHT_SIGNAL: "Cliff FR",
    create.CLIFF_RIGHT_SIGNAL: "Cliff R",
    create.ENCODER_LEFT: "Encoder L",
    create.ENCODER_RIGHT: "Encoder R",
    create.DIRT_DETECTED: "Dirt",
}

SENSORS_TO_POLL = [
    create.WALL_SIGNAL, create.WALL_IR_SENSOR,
    create.LEFT_BUMP, create.RIGHT_BUMP,
    create.ENCODER_LEFT, create.ENCODER_RIGHT,
    create.CLIFF_LEFT_SIGNAL, create.CLIFF_FRONT_LEFT_SIGNAL,
    create.CLIFF_FRONT_RIGHT_SIGNAL, create.CLIFF_RIGHT_SIGNAL,
    create.DIRT_DETECTED,
]


def print_help():
    print("\n--- Roomba CLI Controller ---")
    print("  w/s  — forward / backward (toggle, press again to stop)")
    print("  a/d  — rotate left / right (toggle, press again to stop)")
    print("  x    — stop all movement")
    print("  +/-  — increase / decrease speed")
    print("  m    — toggle main brush")
    print("  v    — toggle vacuum")
    print("  o    — toggle side brush")
    print("  space — reset pose")
    print("  q    — quit")
    print()


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else None

    robot = create.Create(port)
    robot.toSafeMode()
    robot.resetPose()

    fwd_speed = MAX_FORWARD / 2
    rot_speed = MAX_ROTATION / 2

    robot_dir = 0
    robot_rot = 0
    side_brush = 0
    main_brush = 0
    vacuum = 0

    prev_senses = {}

    print_help()
    print("Speed: fwd={:.0f} rot={:.0f}".format(fwd_speed, rot_speed))

    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())

        while True:
            # Check for keypress with timeout so sensor loop continues
            ready, _, _ = select.select([sys.stdin], [], [], 0.2)
            if ready:
                key = sys.stdin.read(1)
                update_roomba = False

                if key == 'q':
                    break
                elif key == 'w':
                    robot_dir = 0 if robot_dir == 1 else 1
                    update_roomba = True
                elif key == 's':
                    robot_dir = 0 if robot_dir == -1 else -1
                    update_roomba = True
                elif key == 'a':
                    robot_rot = 0 if robot_rot == 1 else 1
                    update_roomba = True
                elif key == 'd':
                    robot_rot = 0 if robot_rot == -1 else -1
                    update_roomba = True
                elif key == 'x':
                    robot_dir = 0
                    robot_rot = 0
                    update_roomba = True
                elif key == '+' or key == '=':
                    fwd_speed = min(fwd_speed + MAX_FORWARD * SPEED_INC / 100, MAX_FORWARD)
                    rot_speed = min(rot_speed + MAX_ROTATION * SPEED_INC / 100, MAX_ROTATION)
                    update_roomba = True
                    # Print to a new line in raw mode
                    sys.stdout.write("\r\nSpeed: fwd={:.0f} rot={:.0f}\r\n".format(fwd_speed, rot_speed))
                    sys.stdout.flush()
                elif key == '-':
                    fwd_speed = max(fwd_speed - MAX_FORWARD * SPEED_INC / 100, 0)
                    rot_speed = max(rot_speed - MAX_ROTATION * SPEED_INC / 100, 0)
                    update_roomba = True
                    sys.stdout.write("\r\nSpeed: fwd={:.0f} rot={:.0f}\r\n".format(fwd_speed, rot_speed))
                    sys.stdout.flush()
                elif key == 'm':
                    main_brush = 0 if main_brush else 1
                    update_roomba = True
                elif key == 'v':
                    vacuum = 0 if vacuum else 1
                    update_roomba = True
                elif key == 'o':
                    side_brush = 0 if side_brush else 1
                    update_roomba = True
                elif key == ' ':
                    robot.resetPose()
                    sys.stdout.write("\r\nPose reset\r\n")
                    sys.stdout.flush()
                else:
                    # Unrecognized key — restore terminal briefly to print help
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                    print_help()
                    tty.setraw(sys.stdin.fileno())

                if update_roomba:
                    robot.go(robot_dir * fwd_speed, robot_rot * rot_speed)
                    robot.motors(side_brush, main_brush, vacuum)
                    time.sleep(0.1)

            # Poll sensors
            try:
                senses = robot.sensors(list(SENSORS_TO_POLL))
            except Exception:
                sys.stdout.write("\r\n! Sensor read error\r\n")
                sys.stdout.flush()
                continue

            # Print only changed values
            changed = []
            for sid in SENSORS_TO_POLL:
                val = senses.get(sid)
                if val != prev_senses.get(sid):
                    name = SENSOR_NAMES.get(sid, str(sid))
                    changed.append("{}={}".format(name, val))
            if changed:
                sys.stdout.write("\r\n" + "  ".join(changed) + "\r\n")
                sys.stdout.flush()
            prev_senses = dict(senses)

    except Exception as err:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        print("\nError:", err)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        robot.go(0, 0)
        robot.close()
        print("\nDisconnected.")


if __name__ == '__main__':
    main()
