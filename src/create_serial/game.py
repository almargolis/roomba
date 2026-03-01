#
# game.py
#
# Simple tester for the Roomba Interface
# from create.py
#
# Usage: roomba-game [port]
#   port is optional - auto-detects if not provided.
# Starts a pygame window from which the
# Roomba can be controlled with w/a/s/d.
# Use this file to play with the sensors.
import sys
import time
import math

from . import create


MAX_FORWARD = 50 # in cm per second
MAX_ROTATION = 200 # in cm per second
SPEED_INC = 10 # increment in percent


def draw_roomba(surface, pygame):
	"""Draw a top-down roomba diagram onto a surface."""
	cx, cy, radius = 290, 220, 180
	# body
	pygame.draw.circle(surface, (180, 180, 180), (cx, cy), radius)
	pygame.draw.circle(surface, (100, 100, 100), (cx, cy), radius, 2)
	# front bumper arc
	pygame.draw.arc(surface, (60, 60, 60),
		(cx - radius, cy - radius, radius*2, radius*2),
		math.radians(-60), math.radians(60), 4)
	# direction indicator
	pygame.draw.circle(surface, (60, 60, 60), (cx, cy - radius + 30), 8)
	# labels
	label_font = pygame.font.SysFont("calibri", 12)
	labels = [
		("LB Left", (100, 120)), ("LB FL", (150, 46)), ("LB CL", (218, 4)),
		("LB CR", (445, 4)), ("LB FR", (475, 38)), ("LB Right", (458, 100)),
		("Wall IR:", (340, 380)), ("Wall Sig:", (340, 400)),
		("L Bump:", (100, 380)), ("R Bump:", (100, 400)),
		("Enc L:", (600, 380)), ("Enc R:", (600, 400)),
		("Cliff L:", (600, 0)), ("Cliff FL:", (600, 19)),
		("Cliff FR:", (600, 38)), ("Cliff R:", (600, 57)),
	]
	for text, pos in labels:
		surface.blit(label_font.render(text, 1, (80, 80, 80)), pos)


def main():
	import pygame

	ROOMBA_PORT = sys.argv[1] if len(sys.argv) > 1 else None

	robot = create.Create(ROOMBA_PORT)
	robot.toSafeMode()

	pygame.init()
	size = width, height = 800, 600
	screen = pygame.display.set_mode(size)
	pygame.display.set_caption('Roomba Test')

	# Fill background
	background = pygame.Surface(screen.get_size())
	background = background.convert()
	background.fill((250, 250, 250))

	font = pygame.font.SysFont("calibri",16)

	lb_left = robot.senseFunc(create.LIGHTBUMP_LEFT)
	lb_front_left = robot.senseFunc(create.LIGHTBUMP_FRONT_LEFT)
	lb_center_left = robot.senseFunc(create.LIGHTBUMP_CENTER_LEFT)
	lb_center_right = robot.senseFunc(create.LIGHTBUMP_CENTER_RIGHT)
	lb_front_right = robot.senseFunc(create.LIGHTBUMP_FRONT_RIGHT)
	lb_right = robot.senseFunc(create.LIGHTBUMP_RIGHT)

	FWD_SPEED = MAX_FORWARD/2
	ROT_SPEED = MAX_ROTATION/2

	robot_dir = 0
	robot_rot = 0
	side_brush = 0
	main_brush = 0
	vacuum = 0

	robot.resetPose()
	px, py, th = robot.getPose()

	sensor_error = False
	try:
		while True:
			try:
				senses = robot.sensors([create.WALL_SIGNAL, create.WALL_IR_SENSOR, create.LEFT_BUMP, create.RIGHT_BUMP, create.ENCODER_LEFT, create.ENCODER_RIGHT, create.CLIFF_LEFT_SIGNAL, create.CLIFF_FRONT_LEFT_SIGNAL, create.CLIFF_FRONT_RIGHT_SIGNAL, create.CLIFF_RIGHT_SIGNAL, create.DIRT_DETECTED])
				sensor_error = False
			except Exception:
				sensor_error = True
				senses = {}
			update_roomba = False
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_w:
						robot_dir+=1
						update_roomba = True
					if event.key == pygame.K_s:
						robot_dir-=1
						update_roomba = True
					if event.key == pygame.K_a:
						robot_rot+=1
						update_roomba = True
					if event.key == pygame.K_d:
						robot_rot-=1
						update_roomba = True
					if event.key == pygame.K_ESCAPE:
						pygame.quit()
						return
					if event.key == pygame.K_SPACE:
						robot.resetPose()
						px, py, th = robot.getPose()
					if event.key == pygame.K_UP:
						update_roomba = True
						FWD_SPEED += MAX_FORWARD*SPEED_INC/100
						if FWD_SPEED>MAX_FORWARD:
							FWD_SPEED = MAX_FORWARD
						ROT_SPEED += MAX_ROTATION*SPEED_INC/100
						if ROT_SPEED > MAX_ROTATION:
							ROT_SPEED = MAX_ROTATION
					if event.key == pygame.K_DOWN:
						update_roomba = True
						FWD_SPEED -= MAX_FORWARD*SPEED_INC/100
						if FWD_SPEED<0:
							FWD_SPEED = 0
						ROT_SPEED -= MAX_ROTATION*SPEED_INC/100
						if ROT_SPEED<0:
							ROT_SPEED = 0
					if event.key == pygame.K_m:
						update_roomba = True
						if (pygame.key.get_mods() & pygame.KMOD_SHIFT) :
							main_brush = 1
						else:
							main_brush = -1

					if event.key == pygame.K_v:
						vacuum = 1
						update_roomba = True

					if event.key == pygame.K_o:
						if (pygame.key.get_mods() & pygame.KMOD_SHIFT):
							side_brush = 1
						else:
							side_brush = -1
						update_roomba = True
				if event.type == pygame.KEYUP:
					if event.key == pygame.K_w or event.key == pygame.K_s:
						robot_dir=0
						update_roomba = True
					if event.key == pygame.K_a or event.key == pygame.K_d:
						robot_rot=0
						update_roomba = True
					if event.key == pygame.K_m:
						main_brush = 0
						update_roomba = True
					if event.key == pygame.K_o:
						side_brush = 0
						update_roomba = True
					if event.key == pygame.K_v:
						vacuum = 0
						update_roomba = True

			if update_roomba == True:
				robot.go(robot_dir*FWD_SPEED,robot_rot*ROT_SPEED)
				robot.motors(side_brush, main_brush, vacuum)
				time.sleep(0.1)

			# done with the actual roomba stuff
			# now print.
			screen.blit(background, (0, 0))
			draw_roomba(screen, pygame)

			# helper to safely read a sensor value
			def sv(key, default="--"):
				return senses.get(key, default)

			def safe_lb(func):
				try:
					return func()
				except Exception:
					return "--"

			#Light Bump
			screen.blit(font.render("{}".format(safe_lb(lb_left)), 1, (10, 10, 10)), (112, 136))
			screen.blit(font.render("{}".format(safe_lb(lb_front_left)), 1, (10, 10, 10)), (159, 62))
			screen.blit(font.render("{}".format(safe_lb(lb_center_left)), 1, (10, 10, 10)), (228, 19))

			screen.blit(font.render("{}".format(safe_lb(lb_center_right)), 1, (10, 10, 10)), (457, 19))
			screen.blit(font.render("{}".format(safe_lb(lb_front_right)), 1, (10, 10, 10)), (484, 54))
			screen.blit(font.render("{}".format(safe_lb(lb_right)), 1, (10, 10, 10)), (469, 115))
			#Wall Sensors
			screen.blit(font.render("{}".format(sv(create.WALL_IR_SENSOR)), 1, (10, 10, 10)), (376, 396))
			screen.blit(font.render("{}".format(sv(create.WALL_SIGNAL)), 1, (10, 10, 10)), (376, 416))
			#Bumpers
			screen.blit(font.render("{}".format(sv(create.LEFT_BUMP)), 1, (10, 10, 10)), (142, 396))
			screen.blit(font.render("{}".format(sv(create.RIGHT_BUMP)), 1, (10, 10, 10)), (142, 416))
			#Encoders
			screen.blit(font.render("{}".format(sv(create.ENCODER_LEFT)), 1, (10, 10, 10)), (635, 396))
			screen.blit(font.render("{}".format(sv(create.ENCODER_RIGHT)), 1, (10, 10, 10)), (635, 416))
			#Cliff Sensors
			screen.blit(font.render("{}".format(sv(create.CLIFF_LEFT_SIGNAL)), 1, (10, 10, 10)), (635, 16))
			screen.blit(font.render("{}".format(sv(create.CLIFF_FRONT_LEFT_SIGNAL)), 1, (10, 10, 10)), (635, 35))
			screen.blit(font.render("{}".format(sv(create.CLIFF_FRONT_RIGHT_SIGNAL)), 1, (10, 10, 10)), (635, 54))
			screen.blit(font.render("{}".format(sv(create.CLIFF_RIGHT_SIGNAL)), 1, (10, 10, 10)), (635, 73))

			screen.blit(font.render(" Fwd speed: {:04.2f} cm/sec (change with Up/Down)".format(FWD_SPEED), 1, (10, 10, 10)), (50, 450))
			screen.blit(font.render(" Rot speed: {:04.2f} cm/sec".format(ROT_SPEED), 1, (10, 10, 10)), (50, 470))

			px, py, th = robot.getPose()
			screen.blit(font.render("Estimated X-Position: {:04.2f} (cm from start)".format(px), 1, (10, 10, 10)), (450, 450))
			screen.blit(font.render("Estimated Y-Position: {:04.2f} (cm from start)".format(py), 1, (10, 10, 10)), (450, 470))
			screen.blit(font.render("  Estimated Rotation: {:03.2f} (in degree)".format(th), 1, (10, 10, 10)), (450, 490))
			screen.blit(font.render("       Dirt Detected: {}".format(sv(create.DIRT_DETECTED)), 1, (10, 10, 10)), (450, 510))

			if sensor_error:
				screen.blit(font.render("WARNING: Incomplete sensor data (dust bin removed?)", 1, (200, 0, 0)), (200, 530))

			screen.blit(font.render("Move Roomba with w/a/s/d, adjust speed with UP/DOWN, reset pos with SPACE, and ESC to quit.", 1, (10, 10, 10)), (10, 560))
			screen.blit(font.render("o activates the sidebrush, m the main, v the vacuum. Holding shift could be used for reversing the the direction of the brushes.", 1, (10, 10, 10)), (10, 575))

			pygame.display.flip()
	except Exception as err:
		print(err)
	finally:
		robot.go(0,0)
		robot.close()


if __name__ == '__main__':
	main()
