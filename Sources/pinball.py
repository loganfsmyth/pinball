
import math

from acrenderer import *

class Pinball(ACRenderer):
  def __init__(self):
    self.keypress = []
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

  def keypressFunc(self, key, x, y):
    [f(key, x, y) for f in self.keypress]
    ACRenderer.keypressFunc(self, key, x, y)

class Paddle(ACObject):
  def __init__(self, dat, r):
    self.angle = 0
    self.direction = -1
    self.side = dat['name'].endswith('-r') and -1 or 1
    self.max_angle = 40
    r.keypress.append(self.keyPress)

    ACObject.__init__(self, dat, r)

  def keyPress(self, key, x, r):
    if (key == 'z' and self.side == 1) or (key == '/' and self.side == -1):
      self.direction = 1

  def update(self, time):
    if (self.angle < self.max_angle and self.direction == 1) or (self.angle > 0 and self.direction == -1):
      self.angle += self.direction*time.microseconds/2000.0

  def draw(self):
    glRotate(self.side * self.angle, 0.0, 1.0, 0.0)
    ACObject.draw(self)
    glRotate(-1*self.side*self.angle, 0.0, 1.0, 0.0)

class Ball(ACObject):
  def __init__(self, dat, r):
    ACObject.__init__(self, dat, r)
    self.velocity = 0

  def update(self, time):
#    print "FPS: %f" % (1000000/time.microseconds)
    self.velocity -= time.microseconds*(math.tan(7*math.pi/180)*6.0)/1000000
    self.location[2] -= time.microseconds*self.velocity/1000000

class Peg(ACObject):
  pass

class RubberTriangle(ACObject):
  pass



if __name__ == '__main__':
  glutInit(sys.argv)
  Pinball().run()

