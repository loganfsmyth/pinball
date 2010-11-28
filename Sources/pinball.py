
import math

from acrenderer import *

class Pinball(ACRenderer):
  def __init__(self):
    self.keypress = []
    ACRenderer.__init__(self, 'Pinball.ac', title="Pinball!!!")

    glLightfv(GL_LIGHT2, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT2, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
    glLightfv(GL_LIGHT2, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    glLightfv(GL_LIGHT2, GL_POSITION, (0, 4.24, 4.24))
    glEnable(GL_LIGHT2)

  def render(self): 
    glTranslatef(0.0, 0.0, -3.0)
    glRotated(45.0, 1.0, 0.0, 0.0)
    ACRenderer.render(self)

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

  def keyFunc(self, direction, key, x, y):
    [f(direction, key, x, y) for f in self.keypress]
    ACRenderer.keyFunc(self, direction, key, x, y)

class Paddle(ACObject):
  def __init__(self, dat, r):
    self.angle = 0
    self.direction = -1
    self.side = dat['name'].endswith('-r') and -1 or 1
    self.max_angle = 40
    r.keypress.append(self.keyPress)

    ACObject.__init__(self, dat, r)

  def keyPress(self, dir, key, x, r):
    if (key == 'z' and self.side == 1) or (key == '/' and self.side == -1):
      self.direction = -1*dir

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
    self.radius = math.sqrt(sum([i*i for i in self.vertices[0]]))

  def update(self, time):
#    print "FPS: %f" % (1000000/time.microseconds)
    self.velocity -= time.microseconds*(math.tan(7*math.pi/180)*6.0)/4000000
    self.location[2] -= time.microseconds*self.velocity/1000000

    s = self.getSurfaces(self.renderer.loaders)
    if s[1]:
      s[1].high = True
      if hasattr(s[1], 'name'):
        print "Hit %s" % s[1].name

  def getSurfaces(self, objs):
    loc = self.location

    (all_closest, all_object, all_dist) = (None, None, 1000000000)

    for o in objs:
      within = True
      (closest, object, dist) = (None, None, 10000000)
      for s in o.surfaces:

        p1 = o.vertices[s['refs'][0][0]]
        n = s['norm']
        # Check if the surface's normal is horizontal
        if abs(n[1]) > 0.05:
          continue

        # Check if the surface's normal faces toward the ball
#        v = self.vecSub(loc, p1)
#        d = self.vecDot(v, n)
#        if d < 0:
#          continue


        D = abs((n[0]*loc[0] + n[1]*loc[1] + n[2]*loc[2]) - (n[0]*(o.location[0]+p1[0]) + n[1]*(o.location[1]+p1[1]) + n[2]*(o.location[2] + p1[2])))

        if D > self.radius:
          within = False
          break

        if D < dist:
          (closest, dist) = (s, D)

      if not within:
        if dist < all_dist:
          (all_closest, all_object, all_dist) = (closest, o, dist)
#        if hasattr(o, 'name'): print "Showing %s" % (o.name, )

      v = self.getSurfaces(o.subobjects)
      if v[2] < dist:
        (all_closest, all_object, all_dist) = v

    return (all_closest, all_object, all_dist)

class Peg(ACObject):
  pass

class RubberTriangle(ACObject):
  pass

if __name__ == '__main__':
  glutInit(sys.argv)
  Pinball().run()

