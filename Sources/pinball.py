
import math

from acrenderer import *

class Pinball(ACRenderer):
  
  def __init__(self):
    ACRenderer.__init__(self, 'Pinball.ac', title="Pinball!!!")
  def getObjectClass(self, dat):
    if dat.has_key('name'):
      if dat['name'].startswith('paddle'):
        return Paddle
      elif dat['name'] == 'ball':
        return Ball
      elif dat['name'] == 'peg':
        return Peg
      elif dat['name'].startswith('triangle'):
        return RubberTriangle

    return ACRenderer.getObjectClass(self, dat)

  def displayFunc(self):
    ACRenderer.displayFunc(self)

class Paddle(ACObject):
  def __init__(self, dat):
    ACObject.__init__(self, dat)

  def draw(self):
    angle = 50

    glRotate(angle, 0.0, 1.0, 0.0)
    ACObject.draw(self)
    glRotate(-1*angle, 0.0, 1.0, 0.0)

class Ball(ACObject):
  def __init__(self, dat):
    ACObject.__init__(self, dat)
    self.velocity = 0

  def update(self, time):
    self.velocity -= time.microseconds*(math.tan(7*math.pi/180)*9.8)/1000000
    self.location[2] -= time.microseconds*self.velocity/1000000

class Peg(ACObject):
  pass

class RubberTriangle(ACObject):
  pass



if __name__ == '__main__':
  glutInit(sys.argv)
  Pinball().run()

