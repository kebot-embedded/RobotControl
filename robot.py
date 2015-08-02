# Robot control! Control With Bluez
# Author: vdwel
#
# This script provides a library for controling dash and dot
#
# Dependencies:
# - You must install the pexpect library, typically with 'sudo pip install pexpect'.
# - You must have bluez installed and gatttool in your path (copy it from the
#   attrib directory after building bluez into the /usr/bin/ location).
#
# License: Released under an MIT license: http://opensource.org/licenses/MIT
import sys
import time
import thread
import pexpect
import os
import select

class robot:
  isDash = False
  data15 = ''
  data18 = ''
  gatt = 1
  btdev = ''
  debug15 = False
  debug18 = False
  readingData = False
  leftDistanceSensor = 0
  rightDistanceSensor = 0
  rearDistanceSensor = 0
  button0 = False
  button1 = False
  button2 = False
  button3 = False
  tilt = 0
  lean = 0
  soundLevel = 0
  clap = False
  headX = 0
  headY = 0
  leftWheel = 0
  rightWheel = 0
  zRotationAcceleration = 0
  deltaZRotationAcceleration = 0
  zAcceleration = 0 # between -2040 and +2040
  deltaXRotationAcceleration = 0
  deltaYRotationAcceleration = 0
  soundDirection = 0
  leftSensorSeesDot = False
  rightSensorSeesDot = False
  dotWasSeen = False
  unknown1 = 0
  WheelDistance = 0

  def __init__(self, btdev, isDash=False):
    self.isDash = isDash
    self.gatt = pexpect.spawn('gatttool -I -t random -b {0}'.format(btdev))
    time.sleep(1)
    self.gatt.sendline('connect')
    self.gatt.expect('Connection successful')
    self.btdev = btdev
    self.startReadingData()

  def disconnect(self):
    self.stopReadingData()
    self.gatt.close()

  def connect(self):
    self.__init__(self.btdev)

  def reset(self):
    self.gatt.sendline('char-write-cmd 0x0013 C803') #reset robot

  def drive(self, distmm, timems=0):
    if abs(distmm) >= 0x4000:
      print("Error distance to big, don't exceed 16384!")
      return
    distmm = 0x4000 + distmm if distmm < 0 else distmm
    distHex = "%0.4X" % distmm
    timeHex = "%0.4X" % timems
    byte6 = distHex[0:2]
    byte1 = distHex[2:4]
    byte4 = timeHex[0:2]
    byte5 = timeHex[2:4]
    byte8 = '81' if distmm < 0 else '80'
    self.gatt.sendline('char-write-cmd 0x0013 23{0}0000{1}{2}{3}00{4}'.format(byte1, byte4, byte5, byte6, byte8))

  def setWheelSpeed(self, speed, turnspeed=0):
    if abs(turnspeed) > 500:
      print("Error turnspeed is max 500!")
      return
    if abs(speed) > 400:
      print("Error speed is max 400!")
      return
    speed = 0x800 + speed if speed < 0 else speed
    turnspeed = 0x800 + turnspeed if turnspeed < 0 else turnspeed
    speedHex = "%0.4X" % speed
    turnspeedHex = "%0.4X" % turnspeed
    byte0 = '02'
    byte1 = speedHex[2:4]
    byte2 = turnspeedHex[2:4]
    byte3 = "%0.2X" % int(bin(int(turnspeedHex[0:2],16))[2:].zfill(3)+bin(int(speedHex[0:2],16))[2:].zfill(3),2)
    self.gatt.sendline('char-write-cmd 0x0013 {0}{1}{2}{3}'.format(byte0, byte1, byte2, byte3))

  def stopWheels(self):
    self.gatt.sendline('char-write-cmd 0x0013 02000000')

  def turn(self,degrees, timems = 0):
    if abs(degrees) > 360:
      print("Degrees should not exceed 360!")
      return
    rawDegrees = degrees * 628/360
    byte7 = 'c0' if rawDegrees < 0 else '00'
    rawDegrees = 0x400 + rawDegrees if rawDegrees < 0 else rawDegrees
    rawDegreesHex = "%0.4X" % rawDegrees
    timeHex = "%0.4X" % timems
    byte4 = timeHex[0:2]
    byte5 = timeHex[2:4]
    byte3 = rawDegreesHex[2:4]
    byte6 = "%0.2X" % int(bin(int(rawDegreesHex[0:2],16))[2:]+'000000',2)
    self.gatt.sendline('char-write-cmd 0x0013 230000{0}{1}{2}{3}{4}80'.format(byte3, byte4, byte5, byte6, byte7))

  def moveHeadY(self, degrees):
    if (degrees < -7) | (degrees > 22):
      print("Head cannot go lower than -7 degrees and higher than 22 degrees.")
      return
    degrees = degrees * 100
    degrees = 0x10000 + degrees if degrees < 0 else degrees
    degreesHex = "%0.4X" % degrees
    self.gatt.sendline('char-write-cmd 0x0013 07{0}'.format(degreesHex))

  def moveHeadX(self, degrees):
    if (degrees < -135) | (degrees > 135):
      print("Head cannot move more than 135 degrees.")
      return
    degrees = degrees * -100
    degrees = 0x10000 + degrees if degrees < 0 else degrees
    degreesHex = "%0.4X" % degrees
    self.gatt.sendline('char-write-cmd 0x0013 06{0}'.format(degreesHex))

  def colorFront(self, red, green, blue):
    self.gatt.sendline('char-write-cmd 0x0013 03{0}{1}{2}'.format("%0.2X"%red, "%0.2X"%green, "%0.2X"%blue))

  def colorLeftEar(self, red, green, blue):
    self.gatt.sendline('char-write-cmd 0x0013 0b{0}{1}{2}'.format("%0.2X"%red, "%0.2X"%green, "%0.2X"%blue))

  def colorRightEar(self, red, green, blue):
    self.gatt.sendline('char-write-cmd 0x0013 0c{0}{1}{2}'.format("%0.2X"%red, "%0.2X"%green, "%0.2X"%blue))

  def colorAll(self, redFront, greenFront, blueFront, redLeft, greenLeft, blueLeft, redRight, greenRight, blueRight):
    self.gatt.sendline('char-write-cmd 0x0013 03{0}{1}{2}0b{3}{4}{5}0c{6}{7}{8}'.format("%0.2X"%redFront, "%0.2X"%greenFront, "%0.2X"%blueFront,\
                                                                  "%0.2X"%redLeft, "%0.2X"%greenLeft, "%0.2X"%blueLeft,\
                                                                  "%0.2X"%redRight, "%0.2X"%greenRight, "%0.2X"%blueRight))

  def tailLight(self, on = True):
    val = 0xFF if on else 0x00
    self.gatt.sendline('char-write-cmd 0x0013 04{0}'.format("%0.2X"%val))

  def eyeLights(self, intensity, eye): #eye is twelve with value each bit represents a led
    self.gatt.sendline('char-write-cmd 0x0013 08{0}09{1}'.format("%0.2X"%intensity, "%0.4X"%eye))

  def startReadingData(self):
    self.gatt.sendline('char-write-cmd 0x0019 0100')
    self.gatt.sendline('char-write-cmd 0x0016 0100')
    self.readingData = True
    thread.start_new_thread(self.updateData, ())

  def updateData(self):
    while self.readingData:
      dataLine = self.gatt.readline()
      handle = 'handle = 0x0018 value: '
      if handle in dataLine:
        dataString =  dataLine[dataLine.index(handle)+len(handle):dataLine.index(handle)+len(handle)+59]
        self.data18=dataString
        if self.debug18:
          print '0x0018 ' + dataString
        dataList =  [int(x,16) for x in dataString.split(' ')]
        self.leftDistanceSensor = dataList[7]
        self.rightDistanceSensor = dataList[6]
        self.rearDistanceSensor = dataList[8]
        head = (dataList[0x12]<<8) + dataList[0x13]
        headX = head & 0b0000000111111111 #select last 9 bits
        headY = (head & 0b1111111000000000) >> 9 #select first 7 bits
        headX = headX - 512 if headX > 255 else headX # signed integer conversie
        headY = headY - 128 if headY > 63 else headY
        self.headX = headX * 135/244 #convert to degrees
        self.headY = headY * 22/49 # convert to degrees
        self.leftWheel = (dataList[0x11]<<8) + dataList[0x10]
        self.rightWheel = (dataList[0x0F]<<8) + dataList[0x0E]
        zRotationAcceleration = (dataList[0x0D]<<8) + dataList[0x0C]
        deltaZRotationAcceleration = zRotationAcceleration - self.zRotationAcceleration
        if abs(deltaZRotationAcceleration) > 0x7FFF:
          if deltaZRotationAcceleration < 0:
            deltaZRotationAcceleration = 0x10000 + deltaZRotationAcceleration
          else:
            deltaZRotationAcceleration = -1 * (0x10000 - deltaZRotationAcceleration)
        self.deltaZRotationAcceleration = deltaZRotationAcceleration
        self.zRotationAcceleration = zRotationAcceleration
        self.deltaXRotationAcceleration = ((dataList[0x04] & 0b1111) << 8) + dataList[0x05]
        self.deltaXRotationAcceleration = self.deltaXRotationAcceleration - 0x1000 if self.deltaXRotationAcceleration > 0x7FF else self.deltaXRotationAcceleration
        self.deltaYRotationAcceleration = ((dataList[0x04] & 0b11110000) << 4) + dataList[0x03]
        self.deltaYRotationAcceleration = self.deltaYRotationAcceleration - 0x1000 if self.deltaYRotationAcceleration > 0x7FF else self.deltaYRotationAcceleration
        self.unknown1 = ((dataList[0x02]) << 8) + dataList[0x02]
        self.unknown1 = self.unknown1 - 0x10000 if self.unknown1 > 0x7FFF else self.unknown1
        self.WheelDistance = (dataList[0x09] & 0b1111 << 12) + (dataList[0x0B] << 8) + dataList[0x0A]
        self.WheelDistance = self.WheelDistance - 0x10000 if self.WheelDistance > 0x7FFF else self.WheelDistance
      handle = 'handle = 0x0015 value: '
      if handle in dataLine:
        dataString =  dataLine[dataLine.index(handle)+len(handle):dataLine.index(handle)+len(handle)+59]
        if self.debug15:
          print '0x0015: ' + dataString
        dataList =  [int(x,16) for x in dataString.split(' ')]
        self.debug15List = dataList
        self.button0 = True if (dataList[8] & 0b00010000) > 0 else False
        self.button1 = True if (dataList[8] & 0b00100000) > 0 else False
        self.button2 = True if (dataList[8] & 0b01000000) > 0 else False
        self.button3 = True if (dataList[8] & 0b10000000) > 0 else False
        self.tilt = ((dataList[0x04] & 0b11110000) << 4) + dataList[0x02]
        self.tilt = self.tilt - 0x1000 if self.tilt > 0x7FF else self.tilt
        self.lean = ((dataList[0x4] & 0b1111) << 8) + dataList[0x03]
        self.lean = self.lean - 0x1000 if self.lean > 0x7FF else self.lean
        self.clap = True if (dataList[0x0B] & 0b00000001) == 1 else False
        self.soundLevel = dataList[0x07]
        self.zAcceleration = (dataList[0x05] << 4)+ dataList[0x06]
        self.zAcceleration = self.zAcceleration - 0x1000 if self.zAcceleration > 0x7FF else self.zAcceleration
        if dataList[0x0F] == 0x04:
          self.soundDirection = (dataList[0x0D] << 8) + dataList[0x0C]
          self.soundDirection = self.soundDirection - 360 if self.soundDirection > 180 else self.soundDirection
        if dataList[0x13] == 0x05:
          self.leftSensorSeesDot = True if dataList[0x11] == 0xAA else False
          self.rightSensorSeesDot = True if dataList[0x12] == 0xAA else False
          self.dotWasSeen = True
        if dataList[0x13] == 0x01:
          if self.dotWasSeen == False:
             self.leftSensorSeesDot = False
             self.rightSensorSeesDot = False
          self.dotWasSeen = False

  def stopReadingData(self):
    self.readingData = False
    self.gatt.sendline('char-write-cmd 0x0019 0000')
    self.gatt.sendline('char-write-cmd 0x0016 0000')

def displaySensorData(robot):
  os.system('clear')
  os.system('setterm -cursor off')
  while not (sys.stdin in select.select([sys.stdin], [], [], 0)[0]):
    print("\033["+str(0)+";"+str(0)+"f")
    print 'left distance sensor     : {0}          '.format(robot.leftDistanceSensor)
    print 'right distance sensor    : {0}          '.format(robot.rightDistanceSensor)
    print 'rear distance sensor     : {0}          '.format(robot.rearDistanceSensor)
    print 'top button               : {0}          '.format(robot.button0)
    print 'button 1                 : {0}          '.format(robot.button1)
    print 'button 2                 : {0}          '.format(robot.button2)
    print 'button 3                 : {0}          '.format(robot.button3)
    print 'tilt                     : {0}          '.format(robot.tilt)
    print 'lean                     : {0}          '.format(robot.lean)
    print 'soundLevel               : {0}          '.format(robot.soundLevel)
    print 'clap                     : {0}          '.format(robot.clap)
    print 'head X                   : {0}          '.format(robot.headX)
    print 'head Y                   : {0}          '.format(robot.headY)
    print 'left wheel position      : {0}          '.format(robot.leftWheel)
    print 'right wheel position     : {0}          '.format(robot.rightWheel)
    print 'wheel distance           : {0}          '.format(robot.WheelDistance)
    print 'z rotation acceleration  : {0}          '.format(robot.zRotationAcceleration)
    print 'delta z rotation         : {0}          '.format(robot.deltaZRotationAcceleration)
    print 'delta x rotation         : {0}          '.format(robot.deltaXRotationAcceleration)
    print 'delta y rotation         : {0}          '.format(robot.deltaYRotationAcceleration)
    print 'z acceleration           : {0}          '.format(robot.zAcceleration)
    print 'sound direction          : {0}          '.format(robot.soundDirection)
    print 'left sensor sees Dot     : {0}          '.format(robot.leftSensorSeesDot)
    print 'right sensor sees Dot    : {0}          '.format(robot.rightSensorSeesDot)
    print 'unknown 1                : {0}          '.format(robot.unknown1)
    print ' '
    print 'Press {enter} to continue.'
  os.system('setterm -cursor on')

