
from OpenGL.GLX import *
from ctypes import cdll
from acrenderer import *


class ACGame(ACRenderer):
  def __init__(self, filename, width = 800, height=600, title='ACGame'):
    self.keypress = []
    self.score = 0

    ACRenderer.__init__(self, filename, width, height, title)

    glLightfv(GL_LIGHT2, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT2, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
    glLightfv(GL_LIGHT2, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    glLightfv(GL_LIGHT2, GL_POSITION, (0, 4.24, 4.24))
    glEnable(GL_LIGHT2)

  def keyFunc(self, direction, key, x, y):
    [f(direction, key, x, y) for f in self.keypress]
    ACRenderer.keyFunc(self, direction, key, x, y)

  def getObjectClass(self, dat):
    c = ACRenderer.getObjectClass(self, dat)
    if c == ACObject:
      return ACGameObject
    return c

  def addPoints(self, points):
    self.score += points
    print self.score

  

class ACGameObject(ACObject):
  def __init__(self, data, r):
    ACObject.__init__(self, data, r)

    self.points = 0
    self.velocity = [0, 0, 0]
    self.collisionFactor = 0.8

    if hasattr(self, 'keyPress') and hasattr(self.keyPress, '__call__'):
      r.keypress.append(self.keyPress)

  def draw(self):
    ACObject.draw(self)

    if hasattr(self, 'high') and self.high:
      glTranslate(0.0, 0.5, 0.0)
      glCallList(self.displaylist)
      glTranslate(0.0, -0.5, 0.0)
      self.high = False

  def getVertices(self):
    return self.vertices

  def hitBy(self, object, surface):
#    self.high = True
    print "%s got hit" % (self.name, )
    self.renderer.addPoints(self.points)

  def update(self, time):
    self.location = self.vecAdd(self.location, self.vecMult(self.velocity, time.microseconds/1000000.0))

    [child.update(time) for child in self.subobjects]

