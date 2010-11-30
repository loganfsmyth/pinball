
from acrenderer import *

class ACGame(ACRenderer):
  def __init__(self, filename, width = 800, height=600, title='ACGame'):
    ACRenderer.__init__(self, filename, width, height, title)

    glLightfv(GL_LIGHT2, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT2, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
    glLightfv(GL_LIGHT2, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    glLightfv(GL_LIGHT2, GL_POSITION, (0, 4.24, 4.24))
    glEnable(GL_LIGHT2)

  def getObjectClass(self, dat):
    c = ACRenderer.getObjectClass(self, dat)
    if c == ACObject:
      return ACGameObject
    return c

class ACGameObject(ACObject):
  def draw(self):
    ACObject.draw(self)

    if hasattr(self, 'high') and self.high:
      glTranslate(0.0, 0.5, 0.0)
      glCallList(self.displaylist)
      glTranslate(0.0, -0.5, 0.0)

