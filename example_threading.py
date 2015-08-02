# Example robot control change btDash and btDot into the values for your robot
# find the bluetooth adress of your robot with the command: hcitool lescan

# Dash will drive around, trying to avoid obstacles while constantly turning his head

from robot import *

btDash = "d4:75:30:ab:02:56" # change these to your robots bt addres
btDot = "D0:C5:55:9F:C5:C4"

dash = robot(btDash)
dash.reset()

running = False

def example():
  global running
  running = True
  thread.start_new_thread(shakeHead, ())
  while not (sys.stdin in select.select([sys.stdin], [], [], 0)[0]):
      dash.setWheelSpeed(200)
      while (dash.leftDistanceSensor < 5) & (dash.rightDistanceSensor < 5) & (not (sys.stdin in select.select([sys.stdin], [], [], 0)[0])):
        pass
      if dash.leftDistanceSensor < dash.rightDistanceSensor:
        dash.turn(-90,1000)
      else:
        dash.turn(90,1000)
      time.sleep(1)
  dash.stopWheels()
  dash.reset()
  running = False
      
def shakeHead():
	global running
	while running:
		dash.moveHeadY(0)
		dash.moveHeadX(90)
		time.sleep(1)
		dash.moveHeadY(0)
		dash.moveHeadX(-90)
		time.sleep(1)

print("Press {enter} to stop demo")
example()
dash.disconnect()