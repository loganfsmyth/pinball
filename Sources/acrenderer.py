

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import Image
import datetime
import math


from acloader import *


class ACRenderer:
  def __init__(self, filename, width = 800, height = 600, title = "ACRenderer"):

    self.currenttime = datetime.datetime.now()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    glutInitWindowSize(width, height)
    glutInitWindowPosition(100, 100)
    self.window = glutCreateWindow(title)

    glutReshapeFunc(self.reshapeFunc)
    glutKeyboardFunc(self.keyDown)
    glutKeyboardUpFunc(self.keyUp)
    glClearColor(0.2, 0.2, 0.2, 0.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING)

    self.reshapeFunc(width, height)
    self.loaders = self.createObjects(ACLoader(filename).objects)
    self.counter = 0

    self.animate(0)

  def animate(self, arg):
    """Timer callback for OpenGL. Used to animate objects"""
    time = datetime.datetime.now()
    d = time - self.currenttime
    self.currenttime = time
    [l.update(d) for l in self.loaders]

    time = datetime.datetime.now()
    print "Update: %dus" % ((time-self.currenttime).microseconds, )

    self.displayFunc()

    self.currenttime = datetime.datetime.now()
    print "Display: %dus" % ((self.currenttime - time).microseconds, )

    glutTimerFunc(10, self.animate, 0)

  def createObjects(self, objs, parent=None):
    """Create all of the python objects based on object data give"""
    objects = []
    for obj in objs:
      inst = self.getObjectClass(obj)(obj, self)
      inst.parent = parent
      inst.position = parent and list(parent.vecAdd(parent.position, inst.location)) or inst.location
      inst.subobjects = self.createObjects(obj['kids'], inst)
      objects.append(inst)

    return objects


  def getObjectClass(self, data):
    """Callback to decide what type of class should be instantiated, based on object data"""
    if data['type'] == 'light':
      return ACLight
    else:
      return ACObject

  def displayFunc(self):
    """Clear the screen, render all items and swap the GL buffers"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)	# Clear The Screen And The Depth Buffer
    glLoadIdentity()
    self.render()
    glutSwapBuffers()

  def render(self):
    """Render the objects loaded into this renderer"""
    [l.render() for l in self.loaders]

  def reshapeFunc(self, w, h):
    """Handle the window resize event"""
    self.width = w
    self.height = h

    if h == 0:
      h = 1

    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(w)/float(h), 0.1, 200.0)
    glMatrixMode(GL_MODELVIEW)

  def keyUp(self, key, x, y):
    """Handle someone releasing a pressed key"""
    self.keyFunc( 1, key, x, y)

  def keyDown(self, key, x, y):
    """Handle someone pressing down a key"""
    self.keyFunc(-1, key, x, y)

  def keyFunc(self, direction, key, x, y):
    """Handle a key press from glut"""
    if key == '\033': # Escape key
      glutDestroyWindow(self.window)
      sys.exit()

  def run(self):
    """Execute the main loop of glut, this will never exit"""
    glutMainLoop()

class ACObject:
  def __init__(self, data, renderer):
    self.debug = False
    self.hidden = False
    self.showNormal = False
    self.useDisplaylist = True
    if data.has_key('name'):
      self.name = data['name']
    else:
      self.name = '__blank__'
    self.renderer = renderer
    self.moving = False
    self.location = list(data['loc'])
    self.type = data['type']
    self.vertices = data['verts']
    self.texture = 0
    if data.has_key('texture'):
      self.__loadTexture(data['texture'])
    self.texfile =  data.has_key('texture') and data['texture'] or ''

    self.surfaces = data['surfaces']
    self.subobjects = []

    self.__processSurfaces()
    self.__genList()

  def __processSurfaces(self):
    """Go through the object's surfaces and calculate normals, centers and object centroid"""
    nv = len(self.vertices)
    if nv == 0:
      return

    # Calculate the centroid of the object
    x = y = z = 0
    for i,j,k in self.vertices:
      x += i
      y += j
      z += k
    self.centroid = ( x/nv, y/nv, z/nv )

    for s in self.surfaces:
      nv = len(s['refs'])

      # can only calculate normal if there are > 2 vertices
      if nv > 2:
        vs = self.vertices
        r = s['refs']

        v0 = vs[r[0][0]]
        v1 = vs[r[1][0]]
        v2 = vs[r[2][0]]

        # Calculate normal using cross product of first three vertices
        vn1 = self.vecSub(v0, v1)
        vn2 = self.vecSub(v0, v2)
        n = self.vecCross(vn1, vn2)
        s['norm'] = self.vecNorm(n)

        # Calculate the center of the surface, used when displaying normals
        tot = (0,0,0)
        for r in s['refs']:
          tot = self.vecAdd(self.vertices[r[0]], tot)
        s['center'] = self.vecMult(tot, 1.0/len(s['refs']))

      else:
        s['norm'] = (0,0,0)
        s['center'] = (0,0,0)

  def vecNorm(self, vec):
    """Normalize a given vector"""
    len = abs(math.sqrt(sum([i**2 for i in vec])))
    if len == 0:
      return (0,0,0)
    return tuple([i/len for i in vec])

  def vecSub(self, v1, v2):
    """Subtract two vectors"""
    return ( v1[0]-v2[0], v1[1]-v2[1], v1[2]-v2[2] )
  def vecAdd(self, v1, v2):
    """Add two vectors"""
    return ( v1[0]+v2[0], v1[1]+v2[1], v1[2]+v2[2] )
  def vecMult(self, v, n):
    """Multiply a vector with a scalar"""
    return ( v[0]*n, v[1]*n, v[2]*n )
  def vecCross(self, v1, v2):
    """Calculate the cross product of two vectors"""
    return ( v1[1]*v2[2] - v1[2]*v2[1], v1[2]*v2[0] - v1[0]*v2[2], v1[0]*v2[1] - v1[1]*v2[0])
  def vecDot(self, v1, v2):
    """Calculate the dot product of two vectors"""
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
  def vecMag(self, v):
    """Calculate the magnitude of a vector"""
    return abs(math.sqrt(sum([i**2 for i in v])))

  def update(self, time):
    """Update the object's position based on a given passed time"""
    [obj.update(time) for obj in self.subobjects]

  def render(self):
    """Draw the object and subobjects based on it's location"""
    if self.hidden:
      return

    glTranslate(self.location[0], self.location[1], self.location[2])
    if self.surfaces:
      self.draw()
    [obj.render() for obj in self.subobjects]
    glTranslate(-1*self.location[0], -1*self.location[1], -1*self.location[2])

  def draw(self):
    """Function to draw the object at the given location"""
    glBindTexture(GL_TEXTURE_2D, self.texture)
    glCallList(self.displaylist)

  def __genList(self, render = False):
    """Generate a displaylist for the object"""

    if not render:
      self.displaylist = glGenLists(1)
      glNewList(self.displaylist, GL_COMPILE)

    for surface in self.surfaces:
      glBegin(GL_POLYGON)

      # Set surface normal
      if surface.has_key('norm'):
        glNormal3dv(surface['norm'])
      mat = surface['material']

      # Set material properties for this surface
      glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE,  mat['rgb'] + (mat['trans'],))
      glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION,  mat['emis'] + (1,))
      glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT,  mat['amb'] + (1,))
      glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR,  mat['spec'] + (1,))
      glMateriali(GL_FRONT_AND_BACK, GL_SHININESS, mat['shi'])

      # render the surface polygon itself
      for ref in surface['refs']:
        glTexCoord2d(ref[1], ref[2])
        glVertex3dv(self.vertices[ref[0]])
      glEnd()

      # If enabled, render the surface's normals 
      if self.showNormal and surface.has_key('norm'):
        c = surface['center']
        glTranslate(c[0], c[1], c[2])
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0, 0, 0))
        glBegin(GL_LINES)
        glVertex3dv((0,0,0))
        glVertex3dv(self.vecMult(surface['norm'], 0.05))
        glEnd()
        glTranslate(-1*c[0], -1*c[1], -1*c[2])
    if not render:
      glEndList()

  def __loadTexture(self, file):
    """Loads the object's texture file into an openGL texture object"""

    try:
      image = Image.open(file)
    except:
      print "Failed to load texture %s" % file
      return

    # read image data as raw pixel data
    ix = image.size[0]
    iy = image.size[1]
    image = image.tostring("raw", "RGBX", 0, -1)

    # Generate an openGL texture based on the raw texture data
    self.texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, self.texture)
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)
    glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

class ACLight(ACObject):
  """Specialized class that creates an OpenGL light at the specified location"""
  def __init__(self, data, r):
    ACObject.__init__(self, data, r)
    glLightfv(GL_LIGHT1, GL_AMBIENT, (0.4, 0.4, 0.4, 1.0))
    glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.4, 0.4, 0.4, 1.0))
    glLightfv(GL_LIGHT1, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    glLightfv(GL_LIGHT1, GL_POSITION, self.location)
    glEnable(GL_LIGHT1)

if __name__ == "__main__":
  glutInit(sys.argv)

  if (len(sys.argv) != 2):
    print "Usage: acrenderer.py <filename>"
    sys.exit(0)

  ren = ACRenderer(sys.argv[1])
  ren.run()
