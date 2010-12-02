"""OpenGL Pinball

Usage: python pinball.py [options]

Options:
 -m ..., --mode=...     Run the game in a specific view mode (0 = Front angle, 1 = Top view, 2 = Ball View)
 -s ..., --start=...    The number of the starting pad for the ball
 -v ..., --vel=...      An initial velocity x,y
 -h, --help             Display this meun
 -d                     Show debug output
"""

"""
TODO:
 * Paddle collision
 * Point rendering


"""
import math
import getopt
from acgame import *

class Pinball(ACGame):
  def __init__(self, settings):
    self.starting = {}
    self.ball = None
    self.viewMode = settings['mode'] # 0 = angle, 1 = top, 2 = ball view

    ACGame.__init__(self, 'Pinball0_5.ac', title="Pinball!!!")
    self.ball.location = list(self.starting['start%d'%settings['start']].position)
    self.ball.velocity = settings['velocity']

  def render(self):
    if self.viewMode == 0:
      glTranslatef(0.0, 0.0, -3.0)
      glRotated(45.0, 1.0, 0.0, 0.0)


    ACGame.render(self)

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
      elif dat['name'] == 'drop':
        return Drop
      elif dat['name'] == 'dropitem':
        return DropItem
      elif dat['name'] == 'bumperbase':
        return Bumper
      elif dat['name'].startswith('start'):
        return StartPoint

    return ACGame.getObjectClass(self, dat)

  def displayFunc(self):
    ACGame.displayFunc(self)

class Paddle(ACGameObject):
  def __init__(self, dat, r):
    self.angle = 0
    self.direction = -1
    self.side = dat['name'].endswith('-r') and -1 or 1
    self.max_angle = 40

    ACGameObject.__init__(self, dat, r)

    self.calcVerts = []

  def keyPress(self, dir, key, x, r):
    if (key == 'z' and self.side == 1) or (key == '/' and self.side == -1):
      self.direction = -1*dir

  def __inMotion(self):
    return (self.angle < self.max_angle and self.direction == 1) or (self.angle > 0 and self.direction == -1)

  def update(self, time):
    if self.__inMotion():
      self.angle += self.direction*time.microseconds/2000.0
      self.calcVerts = []

    if self.angle < 0:
      self.angle = 0
    elif self.angle > self.max_angle:
      self.angle = self.max_angle

  def draw(self):
    glRotate(self.side * self.angle, 0.0, 1.0, 0.0)
    ACGameObject.draw(self)
    glRotate(-1*self.side*self.angle, 0.0, 1.0, 0.0)

  def getVertices(self):
    if not self.calcVerts:
      a = self.angle*math.pi/180
      self.calcVerts = [(v[0]*math.cos(a) - v[2]*math.sin(a), v[1], v[2]*math.cos(a) - v[0]*math.sin(a)) for v in self.vertices]

    return self.calcVerts

  def hitBy(self, object, surface):
    if self.__inMotion():
      mult = 0.2
      object.velocity = list(self.vecAdd(object.velocity, self.vecMult(surface['norm'], mult)))
    ACGameObject.hitBy(self, object, surface)

class Ball(ACGameObject):
  def __init__(self, dat, r):
    ACGameObject.__init__(self, dat, r)
    r.ball = self

    self.radius = math.sqrt(sum([i*i for i in self.vertices[0]]))

    self.fps = []

  def update(self, time):
    self.fps.append(1000000/time.microseconds)
    print "FPS: %f" % (sum(self.fps)/len(self.fps), )

    speed = self.vecMag(self.velocity)
    # Check for collision based on current position and velocity
    (surface, object, distance) = self.getClosestSurface()
    if object and not speed == 0.0:
      n = surface['norm']

      # move back along path to just before collision with surface
      mv =  0.004 + self.radius - distance
      self.location = self.vecSub(self.location, self.vecMult(self.velocity, mv/speed))

      # calculate new velocity reflected off the surface normal
      mag = -2*self.vecDot(n, self.velocity)/speed
      new_vel = self.vecAdd(self.velocity, self.vecMult(n,mag))

      # set new velocity and scale, plus account for velocity changes during previous vector calculations
      new_vel = self.vecMult(new_vel, speed/self.vecMag(new_vel))

      self.velocity = list(self.vecMult(new_vel, object.collisionFactor))

#      print "Hit %s %s" % (object.name, object.hidden)

      object.hitBy(self, surface)
    else:
      # Cap the speed so it doesn't get too crazy
      if False and speed > 1.5:
        self.velocity = list(self.vecMult(self.velocity, 1.5/self.vecMag(self.velocity)))

      # Apply some gravity
      self.velocity[2] += time.microseconds*(math.tan(7*math.pi/180)*6.0)/500000

    ACGameObject.update(self, time)

  def getClosestSurface(self, objs = None):
    """Get the closest surface and object based on a list of objects"""
    if objs == None:
      objs = self.renderer.loaders

    dbg = False

    (surface, object, dist) = (None, None, float('inf'))

    # Check every object to find which has the closest surface
    for o in objs:
      if o == self or o.hidden:
        continue

      if o.name == 'paddle-r':
#        self.debug = True
#        print "-------------------------------"
        dbg = True

      # Check the object first
      v = self.getClosestObjectSurface(o)
      if abs(v[1]) < abs(dist):
        (surface, object, dist) = (v[0], o, v[1])
      # Then check the object's children
      v = self.getClosestSurface(o.subobjects)

      if abs(v[2]) < abs(dist):
        (surface, object, dist) = v

      if dbg:
        dbg = False
        self.debug = False

    return (surface, object, dist)

  def getClosestObjectSurface(self, obj):
    """Get the closest surface of a given object"""
    dbg = self.debug

    if dbg: print "Checking surfaces of %s" % obj.name

    (surface, dist) = (None, float('inf'))
    if len(obj.surfaces) < 3:
      return (surface, dist)
    loc = self.location

    verts = obj.getVertices()

    outside = False
    for s in obj.surfaces:
      if dbg: print "Checking %s" % (s, )
      p1 = verts[s['refs'][0][0]]
      n = s['norm']
      # Check if the surface's normal is horizontal
      if abs(n[1]) > 0.05:
        if dbg: print "Discarding, not vertical"
        continue

      # Calculate signed distance from the plane
      D = ((n[0]*loc[0] + n[1]*loc[1] + n[2]*loc[2]) - (n[0]*(obj.position[0]+p1[0]) + n[1]*(obj.position[1]+p1[1]) + n[2]*(obj.position[2] + p1[2])))

      if dbg: print "Distance: %f Current: %f" % (D, dist)

      # If ball farther than radius, it cannot be inside, so break
      if D > self.radius:
        outside = True
        if dbg: print "object is outside, breaking"
        break

      # Use abs to find the surface that the ball is closest to
      if abs(D) < abs(dist):
        if dbg: print "Surface is at distance %f, less that %f" % (D, dist)
        (surface, dist) = (s, D)

    # If we broke, it is outside the object
    if outside:
      return (None, float('inf'))

    if dbg: print "Final Surface: dist: %f surf:%s" % (dist, surface)
    return (surface, dist)

class Peg(ACGameObject):
  def __init__(self, data, r):
    ACGameObject.__init__(self, data, r)
    self.collisionFactor = 0.95
    self.points = 100


class RubberTriangle(ACGameObject):
  def __init__(self, data, r):
    ACGameObject.__init__(self, data, r)
    self.collisionFactor = 1.2
    self.points = 50


class Drop(ACGameObject):
  def __init__(self, data, r):
    ACGameObject.__init__(self, data, r)
    self.count = 0

  def childHit(self, child):
    self.count += 1
    child.points = 500

    if self.count == 3:
      child.points = 5000
      self.count = 0
      for o in self.subobjects:
        o.hidden = False

class DropItem(ACGameObject):
  def __init__(self, data, r):
    ACGameObject.__init__(self, data, r)
    self.collisionFactor = 0.7

  def hitBy(self, obj, surface):
    self.hidden = True
    self.parent.childHit(self)
    ACGameObject.hitBy(self, obj, surface)

class Bumper(ACGameObject):
  def __init__(self, data, r):
    ACGameObject.__init__(self, data, r)
    self.collisionFactor = 1.2
    self.points = 200

class StartPoint(ACGameObject):
  def __init__(self, data, renderer):
    ACGameObject.__init__(self, data, renderer);
    renderer.starting[self.name] = self



if __name__ == '__main__':
  glutInit(sys.argv)
  settings = {
    'mode': 0,
    'start': 0,
    'velocity': [0,0,-3.0],
  }

  try:
    opts, args = getopt.getopt(sys.argv[1:], 'm:s:v:h', ["mode=", "start=", "vel=", "help"])
  except getopt.GetoptError:
    print __doc__
    sys.exit(2)

  for opt, arg in opts:
    if opt in ('-m', '--mode'):
      settings['mode'] = int(arg)
    elif opt in ('-s', '--start'):
      settings['start'] = int(arg)
    elif opt in ('-v', '--vel'):
      v = arg.split(',')
      settings['velocity'] = (float(v[0]), 0, float(v[1]))
    elif opt in ('-h', '--help'):
      print __doc__
      sys.exit()

  Pinball(settings).run()

