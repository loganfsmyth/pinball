
from acrenderer import *


class ACGame(ACRenderer):
  """Game specific class that builds functionality on the static renderer"""
  def __init__(self, filename, width = 800, height=600, title='ACGame', wireframe=False):
    self.keypress = []  # List of functions to trigger when key is pressed
    self.score = 0      # The current game score

    ACRenderer.__init__(self, filename, width, height, title, wireframe)

    # Configure basic overhead light
    glLightfv(GL_LIGHT2, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT2, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
    glLightfv(GL_LIGHT2, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    glEnable(GL_LIGHT2)

  def render(self):
    # Render light above current view location
    glLightfv(GL_LIGHT2, GL_POSITION, (0, 4.24, 4.24))
    ACRenderer.render(self)

  def keyFunc(self, direction, key, x, y):
    """When a key is pressed, we call and object callbacks that registered a keypress callback"""
    [f(direction, key, x, y) for f in self.keypress]
    ACRenderer.keyFunc(self, direction, key, x, y)

  def getObjectClass(self, dat):
    """Override basic object so all objects are ACGameObjects"""
    c = ACRenderer.getObjectClass(self, dat)
    if c == ACObject:
      return ACGameObject
    return c

  def addPoints(self, points):
    """Add to total score"""
    self.score += points

class ACGameObject(ACObject):
  """Base game object class that handles points and animating motion due to velocity"""
  def __init__(self, data, r):
    ACObject.__init__(self, data, r)

    self.passive = False    # By default the ball hits everything
    self.points = 0
    self.velocity = [0, 0, 0]
    self.collisionFactor = 0.85   # Factor to multiple the ball velocity by after hitting this object

    # If this class or a subclass has a keyPress function, register it
    if hasattr(self, 'keyPress') and hasattr(self.keyPress, '__call__'):
      r.keypress.append(self.keyPress)

  def hitBy(self, object, surface):
    """Record points due to a hit"""
    self.renderer.addPoints(self.points)

  def update(self, time):
    """Update location based on velocity and time"""
    self.location = self.vecAdd(self.location, self.vecMult(self.velocity, time.microseconds/1000000.0))

    [child.update(time) for child in self.subobjects]

