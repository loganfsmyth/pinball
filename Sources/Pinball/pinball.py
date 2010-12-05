"""OpenGL Pinball by Logan Smyth and Danny Sarraf

Usage: python pinball.py [options]

Options:
 -g ..., --game=...     Specify different game model ac file
 -o ..., --offset=...   The initial offset from the start point x,y
 -m ..., --mode=...     Run the game in a specific view mode (0 = Front angle, 1 = Top view, 2 = Ball View)
 -s ..., --start=...    The number of the starting pad for the ball
 -v ..., --vel=...      An initial velocity x,y
 -w, --wire             Display model as a wireframe
 -h, --help             Display this meun
 -d, --debug            Show debug output
"""

import math
import getopt
from acgame import *

class Pinball(ACGame):
  def __init__(self, settings):
    self.starting = {}  # lookup for starting points
    self.ball = None    # reference to the child ball
    self.viewMode = settings['mode'] # 0 = angle, 1 = top, 2 = ball view
    self.paddles = {}   # reference to l and r paddles
    self.done = True    # The round is complete
    self.ball_count = 0 # the number of balls left in the round

    ACGame.__init__(self, settings['gamefile'], title="Pinball!!!", wireframe=settings['wireframe'])

    # Set ball data from settings
    self.startVelocity = settings['velocity']
    self.startLocation = self.starting['start%d'%settings['start']].position
    self.startOffset = settings['offset']

    # Set key for launching the ball
    self.launchKey = settings['keys']['fire']

    # Create the right-click menu for changing keys
    menu = glutCreateMenu(self.paddleSetKey)
    glutAddMenuEntry("Change Right Key", 1)
    glutAddMenuEntry("Change Left Key", -1)
    glutAddMenuEntry("Change Launch Key", 2)
    glutAttachMenu(GLUT_RIGHT_BUTTON)

    # Set the keys used, connecting paddles with keys
    self.paddles['l'].key = settings['keys']['l']
    self.paddles['r'].key = settings['keys']['r']

    # trigger game-over to wait for new round start
    self.gameOver()

  def gameOver(self):
    """"Set the status variables to signify the end of a round"""
    self.done = True
    self.ball.hidden = True
    self.ball_count = 5

  def nextBall(self):
    """Set up the ball at the starting point and start round"""
    self.done = False
    self.ball.location = list(self.ball.vecAdd(self.startLocation, self.startOffset))
    self.ball.velocity = list(self.startVelocity)
    self.ball.hidden = False

  def roundComplete(self):
    """A round is complete, the ball reached the bottom"""
    self.ball.hidden = True

    if self.ball_count == 0:
      self.gameOver()

  def roundStart(self):
    """Start a new round, init score and such"""
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
    """Render the whole game"""

    if self.viewMode == 0:
      # 45 degree view
      glTranslatef(0.0, 0.0, -3.0)
      glRotated(45.0, 1.0, 0.0, 0.0)
    elif self.viewMode == 1:
      # rotate to look straight down at the board
      glTranslatef(0.0, 0.0, -3.0)
      glRotated(90.0, 1.0, 0.0, 0.0)
      pass
    elif self.viewMode == 2:
      # Make the view follow the ball
      v = self.ball.velocity
      if not v[2] == 0:
        factor = (v[2] > 0) and math.pi or 0
        a = math.atan(v[0]/v[2]) + factor
        glRotated(a*-180/math.pi, 0.0, 1.0, 0.0)

      p = self.ball.location
      glTranslatef(-1*p[0], -0.1, -1*p[2])


    # Render the scene now that the view is configured
    ACGame.render(self)

    glDisable(GL_LIGHTING)
    glColor3f(0.0, 0.0, 0.0)

    # render text for score and fps and balls remaining
    self.set2D()
    if self.done:
      self.displayString((-2.5, 0.0, 14.0), "Press space to Start")
    elif self.ball.hidden:
      self.displayString((-2.5, 0.0, 14.0), "Press space to continue")

    self.displayString((2.0, 0.0, 22.0), "FPS: %s" % self.fps)
    self.displayString((-2.5, 0.0, 22.0), "Remaining: %d" % self.ball_count)
    self.displayString((-2.5, 0.0, 19.0), "Score: %d" % self.score)


  def getObjectClass(self, dat):
    """Get the Class to use for a given object, based on the AC3D object name"""
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
      elif dat['name'] == 'spinner':
        return Spinner

    return ACGame.getObjectClass(self, dat)



  def set2D(self):
    """Set up a 2D ortho view of the board"""
    height = 2.4   # rough estimate of model depth
    wid = height*self.width/self.height
    glOrtho(-wid/2, wid/2, -height/2, height/2, -20, 20)

  def set3D(self):
    """Set up a 3d perspective view of the board"""
    gluPerspective(45.0, float(self.width)/float(self.height), 0.1, 100.0)

  def reshapeFunc(self, w, h):
    """Handle the window resize event"""
    self.width = w
    self.height = h

    if h == 0:
      h = 1

    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    if self.viewMode == 1:
      self.set2D()
    else:
      self.set3D()

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

  def keyDown(self, key, x, y):
    """Key press handler"""

    # m key hard coded to toggle the view mode
    if key == 'm':
      self.viewMode = (self.viewMode + 1)%3
      self.reshapeFunc(self.width, self.height)

    # Check for ball launch, and start round
    elif key == self.launchKey:
      self.roundStart()
      pass

    # If it is None, the menu option was selected, so save the first key pressed
    elif self.launchKey is None:
      self.launchKey = key

    ACGame.keyDown(self, key, x, y)


  def paddleSetKey(self, type):
    """Menu callback for right-click menu"""
    if type == 1:
      # right
      self.paddles['r'].waiting = True

    elif type == -1:
      # left
      self.paddles['l'].waiting = True

    elif type == 2:
      self.launchKey = None









class Paddle(ACGameObject):
  """Paddle class that manages the behavior of the paddle rendered in the game

  Rotates the vertices of the object based on angle, and recognizes key presses and such
  """

  def __init__(self, dat, r):
    self.angle = 0        # Current angle of paddle
    self.direction = -1   # Current direction of motion (up or down)
    self.side = dat['name'].endswith('-r') and -1 or 1    # Control which direction each paddle rotates
    self.max_angle = 40   # Max allowed angle of paddle
    self.key = None       # the key to watch for to control this paddle
    self.waiting = False  # The paddle has no key selected, this means it should grab the next key pressed
    self.calcVerts = []   # The computed rotated vertices

    # set reference to paddle in renderer
    r.paddles[dat['name'][-1]] = self

    ACGameObject.__init__(self, dat, r)

  def keyPress(self, dir, key, x, y):
    """Key press handler for paddle"""
    if self.waiting:
      self.key = key
      self.waiting = False
    if self.key == key:
      self.direction = -1*dir

  def __inMotion(self):
    return (self.angle < self.max_angle and self.direction == 1) or (self.angle > 0 and self.direction == -1)

  def update(self, time):
    """Animation function. Updates the angle based on the elapsed time"""
    if self.__inMotion():
      self.angle += self.direction*time.microseconds/2000.0
      self.calcVerts = []
      self.getVertices()

    if self.angle < 0:
      self.angle = 0
    elif self.angle > self.max_angle:
      self.angle = self.max_angle

  def draw(self):
    """Draw the paddle rotated by the given angle"""
    glRotate(self.side * self.angle, 0.0, 1.0, 0.0)
    # Renders using the a standard display list
    ACGameObject.draw(self)
    glRotate(-1*self.side*self.angle, 0.0, 1.0, 0.0)

  def getVertices(self):
    """Override default vertex function to return computed rotated vertices"""
    if not self.calcVerts:
      # Multiple each vertex by the rotation matrix
      a = -1*self.side*self.angle*math.pi/180
      self.calcVerts = [(v[0]*math.cos(a) - v[2]*math.sin(a), v[1], v[2]*math.cos(a) + v[0]*math.sin(a)) for v in self.vertices]
      self.processSurfaces()

    return self.calcVerts

  def hitBy(self, object, surface):
    """Callback when hit by ball"""
    #If the paddle is moving and the ball hits it, it adds a bit of the surface normal vector to the ball's velocity
    if self.__inMotion():
      mult = 1.5
      object.velocity = list(self.vecAdd(object.velocity, self.vecMult(surface['norm'], mult)))
    ACGameObject.hitBy(self, object, surface)






class Ball(ACGameObject):
  """Ball class that calculates collisions with other renderer objects
  and other fanciness
  """

  def __init__(self, dat, r):
    ACGameObject.__init__(self, dat, r)
    r.ball = self # Set ball reference on renderer

    self.hidden = True
    self.radius = math.sqrt(sum([i*i for i in self.vertices[0]]))

  def update(self, time):
    """Animation callback for ball, checks for collisions and modifies velocity of ball"""
    if self.hidden:
      return

    speed = self.vecMag(self.velocity)
    # Check for collision based on current position and velocity
    (surface, object, distance) = self.getClosestSurface()
    if object :
      n = surface['norm']

      print "Hit %s" % (object.name, )


      # Passive objects are affected by ball, but have no effect on it
      if not object.passive:

        # move back along path to just before collision with surface
        mv =  0.004 + self.radius - distance
        self.location = self.vecSub(self.location, self.vecMult(self.velocity, mv/speed))

        # calculate new velocity reflected off the surface normal
        mag = -2*self.vecDot(n, self.velocity)/speed
        new_vel = self.vecAdd(self.velocity, self.vecMult(n,mag))

        # set new velocity and scale, plus account for velocity changes during previous vector calculations
        new_vel = self.vecMult(new_vel, speed/self.vecMag(new_vel))

        # scale velocity by collision factor
        self.velocity = list(self.vecMult(new_vel, object.collisionFactor))

      # Trigger the object's hitBy function
      object.hitBy(self, surface)
    
    # Cap the speed so it doesn't get too crazy
    if speed > 3.5:
      self.velocity = list(self.vecMult(self.velocity, 2.0/self.vecMag(self.velocity)))
    # Apply some gravity
    self.velocity[2] += time.microseconds*(math.tan(7*math.pi/180)*6.0)/500000

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
      # Ignore surface if its normal is horizontal
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
  """Peg class to specify basic peg characteristics"""
  def __init__(self, data, r):
    ACGameObject.__init__(self, data, r)
    self.collisionFactor = 0.95
    self.points = 100


class RubberTriangle(ACGameObject):
  """Triangle class to specify triangle characteristics"""
  def __init__(self, data, r):
    ACGameObject.__init__(self, data, r)
    self.collisionFactor = 1.0
    self.points = 200
    
  def hitBy(self, object, surface):
    """The triangles add a bit of speed to the ball, based on surface normal"""
    mult = 1.0
    object.velocity = list(self.vecAdd(object.velocity, self.vecMult(surface['norm'], mult)))
    ACGameObject.hitBy(self, object, surface)




class Drop(ACGameObject):
  """Parent drop class for each group of three drop items"""
  def __init__(self, data, r):
    ACGameObject.__init__(self, data, r)
    self.count = 0

  def childHit(self, child):
    """Triggered when a drop item is hit, when all three are hit, 
    we add extra points and show all items again
    """
    self.count += 1
    child.points = 500

    if self.count == 3:
      child.points = 5000
      self.count = 0
      for o in self.subobjects:
        o.hidden = False

class DropItem(ACGameObject):
  """Drop item class for basic params and triggers parent event"""
  def __init__(self, data, r):
    ACGameObject.__init__(self, data, r)
    self.collisionFactor = 0.7

  def hitBy(self, obj, surface):
    self.hidden = True
    self.parent.childHit(self) #let the parent know this child was hit
    ACGameObject.hitBy(self, obj, surface)

class Bumper(ACGameObject):
  """Bumper specific settings"""
  def __init__(self, data, r):
    ACGameObject.__init__(self, data, r)
    self.collisionFactor = 1.1
    self.points = 200

class StartPoint(ACGameObject):
  """Starting point class to just let renderer know available starting points"""
  def __init__(self, data, renderer):
    ACGameObject.__init__(self, data, renderer);
    renderer.starting[self.name] = self

class GameOver(ACGameObject):
  """GameOver class to track when the bottom block on the game board gets hit"""
  def hitBy(self, obj, surface):
    self.renderer.roundComplete()


class Spinner(ACGameObject):
  """Fancy spinner class to manage animation and such"""
  def __init__(self, data, renderer):
    ACGameObject.__init__(self, data, renderer);
    self.passive = True   # The ball makes this move, but the ball doesn't bounce off of it
    self.angle = 0        # Current animation angle
    self.speed = 0        # current animation speed

    self.points = 1000    

    self.rot = self.surfaces[3]['norm']   # Rotation axis vector, manually set by looking at file

  def hitBy(self, obj, surface):
    """When hit by ball, start spinning"""
    self.speed = 20

  def update(self, time):
    """Animation function. Increase angle based on speed and slowly decrease speed"""
    self.angle += self.speed*10000/time.microseconds

    self.speed -= 0.1
    if self.speed < 0:
      self.speed = 0

  def draw(self):
    """Render the spinner rotated around the rotation axit"""
    r = self.rot
    glRotate(self.angle, r[0], r[1], r[2])
    ACGameObject.draw(self)
    glRotate(-1*self.angle, r[0], r[1], r[2])



if __name__ == '__main__':
  glutInit(sys.argv)

  # default settings for pinball
  settings = {
    'mode': 0,
    'start': 1,
    'velocity': [0,0,-3.2],
    'offset': [0, 0, 0],
    'debug': False,
    'keys': {
      'l': 'z',
      'r': '/',
      'fire': ' ',
    },
    'gamefile': 'Pinball0_5.ac',
    'wireframe': False,
  }

  # Read command line arguments and override default settings where applicable
  try:
    opts, args = getopt.getopt(sys.argv[1:], 'g:m:s:v:o:hdw', ["game=", "mode=", "start=", "vel=", "offset=", "help", 'debug', 'wire'])
  except getopt.GetoptError:
    print __doc__
    sys.exit(2)

  for opt, arg in opts:
    if opt in ('-m', '--mode'):     # Control the view mode
      settings['mode'] = int(arg)
    elif opt in ('-s', '--start'):  # Control default start point
      settings['start'] = int(arg)
    elif opt in ('-v', '--vel'):    # Control default velocity
      v = arg.split(',')
      settings['velocity'] = [float(v[0]), 0, float(v[1])]
    elif opt in ('-o', '--offset'): # Control default offset from starting
      o = arg.split(',')
      settings['offset'] = [float(o[0]), 0, float(o[1])]
    elif opt in ('-g', '--game'):   # Set game board model file
      settings['gamefile'] = arg
    elif opt in ('-w', '--wire'):   # Display board in wireframe mode
      settings['wireframe'] = True
    elif opt in ('-h', '--help'):   # Display usage
      print __doc__
      sys.exit()
    elif opt in ('-d', '--debug'):  # This does nothing :P
      settings['debug'] = bool(arg)

  # Exec main loop
  Pinball(settings).run()

