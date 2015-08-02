#Example robot control change btDash and btDot into the values for your robot
#find the bluetooth adress of your robot with the command: hcitool lescan

from robot import *

btDash = "d4:75:30:ab:02:56"
btDot = "D0:C5:55:9F:C5:C4"

dash = robot(btDash)
dash.reset()

#Show sensor data
displaySensorData(dash)


def demo1():
  sd = 0
  while True:
    if sd != dash.soundDirection:
      dash.turn(dash.soundDirection)
      time.sleep(3)
      dash.drive(400)
    sd = dash.soundDirection

def demo2():
  for i in range(0, 500, 5):
    dash.setWheelSpeed(0,i)
  for i in range(500, -500, -5):
    dash.setWheelSpeed(0,i)
  for i in range(-500, 0, 5):
    dash.setWheelSpeed(0,i)
  dash.setWheelSpeed(0,0)

#    time.sleep(0.001)

#dot = robot(btDot, False)
#dot.reset()


## wait for sound
#while dash.soundLevel == 0:
#  pass

##  Drive maximum speed
#dash.setWheelSpeed(400)

## wait until object in front
#while (dash.leftDistanceSensor < 5) & (dash.rightDistanceSensor < 5):
#  pass

#dash.stopWheels()
#dash.drive(100,166)

