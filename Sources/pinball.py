"""OpenGL Pinball

Usage: python pinball.py [options]

Options:
 -m ..., --mode=...     Run the game in a specific view mode (0 = Front angle, 1 = Top view, 2 = Ball View)
 -s ..., --start=...    The number of the starting pad for the ball
 -v ..., --vel=...      An initial velocity x,y
 -h, --help             Display this meun
 -d                     Show debug output
"""

import math
import getopt
from acgame import *

class Pinball(ACGame):
  def __init__(self, settings):
    self.starting = {}
    self.ball = None
    self.viewMode = settings['mode'] # 0 = angle, 1 = top, 2 = ball view
    self.paddles = {}
    self.done = True
    self.ball_count = 0
    ACGame.__init__(self, 'Pinball0_5.ac', title="Pinball!!!")
    self.startVelocity = settings['velocity']
    self.startLocation = self.starting['start%d'%settings['start']].position
    self.startOffset = settings['offset']
    self.launchKey = settings['keys']['fire']


    menu = glutCreateMenu(self.paddleSetKey)
    glutAddMenuEntry("Change Right Key", 1)
    glutAddMenuEntry("Change Left Key", -1)
    glutAddMenuEntry("Change Launch Key", 2)


    glutAttachMenu(GLUT_RIGHT_BUTTON)

    self.paddles['l'].key = settings['keys']['l']
    self.paddles['r'].key = settings['keys']['r']

    self.gameOver()

  def gameOver(self):
    self.done = True
    self.ball.hidden = True
    self.ball_count = 5

  def nextBall(self):
    self.done = False
    self.ball.location = list(self.ball.vecAdd(self.startLocation, self.startOffset))
    self.ball.velocity = list(self.startVelocity)
    self.ball.hidden = False

  def roundComplete(self):
    self.ball.hidden = True

    if self.ball_count == 0:
      self.gameOver()

  def roundStart(self):
    if self.done:
      self.ball_count = 5
      self.score = 0
      self.nextBall()
    elif (not self.ball.hidden) and self.ball_count == 0:
      self.roundComplete()
    else:
      self.nextBall()

    self.ball_count -= 1

  def render(self):
    if self.viewMode == 0:
      glTranslatef(0.0, 0.0, -3.0)
      glRotated(45.0, 1.0, 0.0, 0.0)
    elif self.viewMode == 1:
      glTranslatef(0.0, 0.0, -3.0)
      glRotated(90.0, 1.0, 0.0, 0.0)
      pass
    elif self.viewMode == 2:
      v = self.ball.velocity
      factor = (v[2] > 0) and math.pi or 0
      a = math.atan(v[0]/v[2]) + factor
      glRotated(a*-180/math.pi, 0.0, 1.0, 0.0)

      p = self.ball.location
      glTranslatef(-1*p[0], -0.1, -1*p[2])

    ACGame.render(self)

    if self.done:
      self.displayString((0.0, 0.0, -4.0), "Press space to Start")
    elif self.ball.hidden:
      self.displayString((0.0, 0.0, -4.0), "Press space to continue")

    self.displayString((0.0, 0.0, -6.0), "Remaining: %d"%self.ball_count)

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
      elif dat['name'] == 'gameover':
        return GameOver

    return ACGame.getObjectClass(self, dat)

  def reshapeFunc(self, w, h):
    """Handle the window resize event"""
    self.width = w
    self.height = h

    if h == 0:
      h = 1

    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    if self.viewMode == 0 or self.viewMode == 2:
      gluPerspective(45.0, float(w)/float(h), 0.1, 100.0)
    elif self.viewMode == 1:
      height = 2.4
      wid = height*self.width/self.height
      glOrtho(-wid/2, wid/2, -height/2, height/2, -20, 20)


    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

  def keyDown(self, key, x, y):
    if key == 'm':
      self.viewMode = (self.viewMode + 1)%3
      self.reshapeFunc(self.width, self.height)
    elif key == self.launchKey:
      self.roundStart()
      pass

    elif self.launchKey is None:
      self.launchKey = key

    ACGame.keyDown(self, key, x, y)

  def paddleSetKey(self, type):
    if type == 1:
      # right
      self.paddles['r'].waiting = True

      pass

    elif type == -1:
      # left
      self.paddles['l'].waiting = True
      pass
    elif type == 2:
      self.launchKey = None


class Paddle(ACGameObject):
  def __init__(self, dat, r):
    self.angle = 0
    self.direction = -1
    self.side = dat['name'].endswith('-r') and -1 or 1
    self.max_angle = 40
    self.key = None
    self.waiting = False
    self.calcVerts = []

    r.paddles[dat['name'][-1]] = self

    ACGameObject.__init__(self, dat, r)

    self.showNormal = True

  def keyPress(self, dir, key, x, y):
    if self.waiting:
      self.key = key
      self.waiting = False
    if self.key == key:
      self.direction = -1*dir

  def __inMotion(self):
    return (self.angle < self.max_angle and self.direction == 1) or (self.angle > 0 and self.direction == -1)

  def update(self, time):
    if self.__inMotion():
      self.angle += self.direction*time.microseconds/2000.0
      self.calcVerts = []
      self.getVertices()

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
      a = -1*self.side*self.angle*math.pi/180
      self.calcVerts = [(v[0]*math.cos(a) - v[2]*math.sin(a), v[1], v[2]*math.cos(a) + v[0]*math.sin(a)) for v in self.vertices]
      self.processSurfaces()


    return self.calcVerts

  def hitBy(self, object, surface):
    if self.__inMotion():
      mult = 2.0
      object.velocity = list(self.vecAdd(object.velocity, self.vecMult(surface['norm'], mult)))
    ACGameObject.hitBy(self, object, surface)






class Ball(ACGameObject):
  def __init__(self, dat, r):
    ACGameObject.__init__(self, dat, r)
    r.ball = self

    self.radius = math.sqrt(sum([i*i for i in self.vertices[0]]))

  def update(self, time):
    if self.hidden:
      return

    speed = self.vecMag(self.velocity)
    # Check for collision based on current position and velocity
    (surface, object, distance) = self.getClosestSurface()
    if object :
      n = surface['norm']

      print "Hit %s" % (object.name, )

      # move back along path to just before collision with surface
      mv =  0.004 + self.radius - distance
      self.location = self.vecSub(self.location, self.vecMult(self.velocity, mv/speed))

      # calculate new velocity reflected off the surface normal
      mag = -2*self.vecDot(n, self.velocity)/speed
      new_vel = self.vecAdd(self.velocity, self.vecMult(n,mag))

      # set new velocity and scale, plus account for velocity changes during previous vector calculations
      new_vel = self.vecMult(new_vel, speed/self.vecMag(new_vel))

      self.velocity = list(self.vecMult(new_vel, object.collisionFactor))

      object.hitBy(self, surface)
    else:
      # Cap the speed so it doesn't get too crazy
      if False and speed > 1.5:
        self.velocity = list(self.vecMult(self.velocity, 1.5/self.vecMag(self.velocity)))

      # Apply some gravity
      self.velocity[2] += time.microseconds*(math.tan(7*math.pi/180)*6.0)/700000

    ACGameObject.update(self, time)

  def getClosestSurface(self, objs = None):
    """Get the closest surface and object based on a list of objects"""
    if objs == None:
      objs = self.renderer.loaders

    (surface, object, dist) = (None, None, float('inf'))

    # Check every object to find which has the closest surface
    for o in objs:
      if o == self or o.hidden:
        continue
      # Check the object first
      v = self.getClosestObjectSurface(o)
      if abs(v[1]) < abs(dist):
        (surface, object, dist) = (v[0], o, v[1])
      # Then check the object's children
      v = self.getClosestSurface(o.subobjects)

      if abs(v[2]) < abs(dist):
        (surface, object, dist) = v

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
      if dbg: print "Checking Norm: %s Center %s" % (s['norm'], s['center'])
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
    self.points = 200


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
  def draw(self):
    pass

class GameOver(ACGameObject):
  def hitBy(self, obj, surface):
    self.renderer.roundComplete()

if __name__ == '__main__':
  glutInit(sys.argv)
  settings = {
    'mode': 0,
    'start': 1,
    'velocity': [0,0,-3.0],
    'offset': [0, 0, 0],
    'debug': False,
    'keys': {
      'l': 'z',
      'r': '/',
      'fire': ' ',
    }
  }

  try:
    opts, args = getopt.getopt(sys.argv[1:], 'm:s:v:o:hd', ["mode=", "start=", "vel=", "offset=", "help", 'debug'])
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
      settings['velocity'] = [float(v[0]), 0, float(v[1])]
    elif opt in ('-o', '--offset'):
      o = arg.split(',')
      settings['offset'] = [float(o[0]), 0, float(o[1])]
    elif opt in ('-h', '--help'):
      print __doc__
      sys.exit()
    elif opt in ('-d', '--debug'):
      settings['debug'] = bool(arg)

  Pinball(settings).run()

