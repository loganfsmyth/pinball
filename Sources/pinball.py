
import math

from acrenderer import *

class Pinball(ACRenderer):
  def __init__(self):
    self.keypress = []

    ACRenderer.__init__(self, 'Pinball.ac', title="Pinball!!!")
#    ACRenderer.__init__(self, 'Pinball0_3.ac', title="Pinball!!!")

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
    self.velocity = [0, 0, 0]
    self.radius = math.sqrt(sum([i*i for i in self.vertices[0]]))
    print "Ball Radius: %f" % self.radius

    self.location[0] = 0.35#0.40
    self.location[2] = -0.35

    self.velocity[2] = 0.2

  def update(self, time):
#    print "FPS: %f" % (1000000/time.microseconds)
    self.velocity[2] += time.microseconds*(math.tan(7*math.pi/180)*6.0)/4000000

    self.location = self.vecAdd(self.location, self.vecMult(self.velocity, time.microseconds/1000000.0))

    (surface, object, distance) = self.getClosestSurface()
    if object:
      n = surface['norm']
#      object.high = True

      factor = self.vecMult(n, 2*distance)
#      print surface
#      print object.name
#      print distance

#      print "Orig Vel: %s" % self.velocity
      self.velocity = list(self.vecMult(self.vecSub(self.velocity, factor), -1))
#      print "New Vel:  %s" % self.velocity

  def getClosestSurface(self, objs = None):
    if objs == None:
      objs = self.renderer.loaders

    (surface, object, dist) = (None, None, float('inf'))

    for o in objs:
      if o == self:
        continue
      v = self.getClosestObjectSurface(o)
      if v[1] < dist:
        (surface, object, dist) = (v[0], o, v[1])

      v = self.getClosestSurface(o.subobjects)
      if v[2] < dist:
        (surface, object, dist) = v

    return (surface, object, dist)

  def getClosestObjectSurface(self, obj):
    (surface, dist) = (None, float('inf'))
    if len(obj.surfaces) == 0:
      return (surface, dist)
    loc = self.location
    obj.high = False
    
    outside = False
    for s in obj.surfaces:
      p1 = obj.vertices[s['refs'][0][0]]
      n = s['norm']
      # Check if the surface's normal is horizontal
      if abs(n[1]) > 0.05:
        continue

      D = ((n[0]*loc[0] + n[1]*loc[1] + n[2]*loc[2]) - (n[0]*(obj.location[0]+p1[0]) + n[1]*(obj.location[1]+p1[1]) + n[2]*(obj.location[2] + p1[2])))

      if D > self.radius:
        outside = True
        break
      if D < dist:
        (surface, dist) = (s, D)

    if outside:
      return (None, float('inf'))
    return (surface, dist)

class Peg(ACObject):
  pass

class RubberTriangle(ACObject):
  pass

if __name__ == '__main__':
  glutInit(sys.argv)
  Pinball().run()

