# Example robot control change btDash and btDot into the values for your robot
# find the bluetooth adress of your robot with the command: hcitool lescan

# Dash will turn to the sound he hears and then drives 40cm towards it

from robot import *

btDash = "d4:75:30:ab:02:56" # change these to your robots bt addres
btDot = "D0:C5:55:9F:C5:C4"

dot = robot(btDot)
dot.reset()

running = False
wait = False

def example():  
  global running
  running = True
  thread.start_new_thread(Disco, ())
  dot.topLight(True)
  while not (sys.stdin in select.select([sys.stdin], [], [], 0)[0]):
    if dot.button0:
        dot.playSound(GOBBLE)
        time.sleep(2)
    if dot.button1:
        dot.playSound(HORSE)
        time.sleep(2)
    if dot.button2:
        dot.playSound(MYSOUND4)
        time.sleep(2)
    if dot.button3:
        dot.playSound(HI)
        time.sleep(2)
    if dot.tilt > 600:
        dot.playSound(UHOH)
        time.sleep(2)
    if dot.lean > 600:
        dot.playSound(DOG)
        time.sleep(2)
    if dot.tilt < -600:
        dot.playSound(FIRESIREN)
        time.sleep(2)
    if dot.lean < -600:
        dot.playSound(JETPLANE)
        time.sleep(3)
  running = False

def Disco():
    global running
    global wait
    red = 16
    green = 71
    blue = 21
    redStep = 10
    greenStep = -15
    blueStep = 5
    while running:
        redStep = -redStep if (red >= 240) | (red<=15) else redStep
        greenStep = -greenStep if (green >= 240) | (green<=15) else greenStep
        blueStep = -blueStep if (blue >= 240) | (blue<=15) else blueStep
        red += redStep
        green += greenStep
        blue += blueStep
        if not wait:
            dot.colorAll(red, green, blue, red, green, blue, red, green, blue)    

print("Press {enter} to stop demo")
example()
dot.disconnect()