

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import Image
import datetime
import math


from acloader import *




class ACRenderer:
  def __init__(self, filename, width = 800, height = 600, title = "ACRenderer"):

    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    glutInitWindowSize(width, height)
    glutInitWindowPosition(100, 100)
    self.window = glutCreateWindow(title)

#    glutDisplayFunc(self.displayFunc)
#    glutIdleFunc(self.idleFunc)
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
    self.currenttime = datetime.datetime.now()
    self.animate(0)

  def animate(self, arg):
#    print self.counter
    self.counter += 1
    time = datetime.datetime.now()
    [l.update(time - self.currenttime) for l in self.loaders]
    self.currenttime = time
    self.displayFunc()
    glutTimerFunc(10, self.animate, 0)


  def createObjects(self, objs, parent=None):
    objects = []
    for obj in objs:
      inst = self.getObjectClass(obj)(obj, self)
      inst.parent = parent
      inst.subobjects = self.createObjects(obj['kids'], inst)
      objects.append(inst)

    return objects


  def getObjectClass(self, data):
    if data['type'] == 'light':
      return ACLight
    else:
      return ACObject

  def displayFunc(self):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)	# Clear The Screen And The Depth Buffer
    glLoadIdentity()
    self.render()
    glutSwapBuffers()

  def render(self):
    [l.render() for l in self.loaders]

  def idleFunc(self):
    self.displayFunc()

  def reshapeFunc(self, w, h):
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
    self.keyFunc( 1, key, x, y)
  def keyDown(self, key, x, y):
    self.keyFunc(-1, key, x, y)

  def keyFunc(self, direction, key, x, y):
    if key == '\033': # Escape key
      glutDestroyWindow(self.window)
      sys.exit()

  def run(self):
    glutMainLoop()

class ACObject:
  def __init__(self, data, renderer):
    self.debug = False
    if data.has_key('name'):
      self.name = data['name']
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

#    if hasattr(self, 'name') and self.name == 'peg':
#      print len(self.vertices)
#      print len(self.surfaces)

  def __processSurfaces(self):
    nv = len(self.vertices)
    if nv == 0:
      return

    x = y = z = 0
    for v in self.vertices:
      x += v[0]
      y += v[1]
      z += v[2]


    self.centroid = ( x/nv, y/nv, z/nv )

    for s in self.surfaces:
      nv = len(s['refs'])
      if nv > 2:
        vs = self.vertices
        r = s['refs']

        v0 = vs[r[0][0]]
        v1 = vs[r[1][0]]
        v2 = vs[r[2][0]]

        vn1 = self.vecSub(v0, v1)
        vn2 = self.vecSub(v0, v2)

        n = self.vecCross(vn1, vn2)
        s['norm'] = self.vecNorm(n)

        tot = (0,0,0)
        for r in s['refs']:
          tot = self.vecAdd(self.vertices[r[0]], tot)

        s['center'] = self.vecMult(tot, 1.0/len(s['refs']))

      else:
        s['norm'] = (0,0,0)
        s['center'] = (0,0,0)

  def vecNorm(self, vec):
    len = abs(math.sqrt(sum([i**2 for i in vec])))
    if len == 0:
      return (0,0,0)
    return tuple([i/len for i in vec])

  def vecSub(self, v1, v2):
    return ( v1[0]-v2[0], v1[1]-v2[1], v1[2]-v2[2] )
  def vecAdd(self, v1, v2):
    return ( v1[0]+v2[0], v1[1]+v2[1], v1[2]+v2[2] )
  def vecMult(self, v, n):
    return ( v[0]*n, v[1]*n, v[2]*n )
  def vecCross(self, v1, v2):
    return ( v1[1]*v2[2] - v1[2]*v2[1], v1[2]*v2[0] - v1[0]*v2[2], v1[0]*v2[1] - v1[1]*v2[0])
  def vecDot(self, v1, v2):
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
  def vecMag(self, v):
    return abs(math.sqrt(sum([i**2 for i in v])))

  def update(self, time):
    [obj.update(time) for obj in self.subobjects]

  def render(self):
    glTranslate(self.location[0], self.location[1], self.location[2])
    if self.surfaces:
      self.draw()
    [obj.render() for obj in self.subobjects]
    glTranslate(-1*self.location[0], -1*self.location[1], -1*self.location[2])

  def draw(self):
    glBindTexture(GL_TEXTURE_2D, self.texture)
    glCallList(self.displaylist)
    if hasattr(self, 'high') and self.high:
      glTranslate(0.0, 0.5, 0.0)
      glCallList(self.displaylist)
      glTranslate(0.0, -0.5, 0.0)

  def __genList(self):
#    if hasattr(self, 'name'):
#      print "Generating %s with %d surfs" % (self.name, len(self.surfaces))

    self.displaylist = glGenLists(1)

    glNewList(self.displaylist, GL_COMPILE)
    for surface in self.surfaces:
      glBegin(GL_POLYGON)
      if surface.has_key('norm'):
        glNormal3dv(surface['norm'])
      mat = surface['material']
      glColor3dv(surface['material']['rgb'])

      glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE,  mat['rgb'] + (mat['trans'],))
      glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION,  mat['emis'] + (1,))
      glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT,  mat['amb'] + (1,))
      glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR,  mat['spec'] + (1,))
      glMateriali(GL_FRONT_AND_BACK, GL_SHININESS, mat['shi'])

      for ref in surface['refs']:
        glTexCoord2d(ref[1], ref[2])
        glVertex3dv(self.vertices[ref[0]])
      glEnd()

      if False and surface.has_key('norm'):
        c = surface['center']
        glTranslate(c[0], c[1], c[2])
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0, 0, 0))
        glBegin(GL_LINES)
        glVertex3dv((0,0,0))
        glVertex3dv(self.vecMult(surface['norm'], 0.05))
        glEnd()
        glTranslate(-1*c[0], -1*c[1], -1*c[2])
    glEndList()

  def __loadTexture(self, file):
    try:
      image = Image.open(file)
    except:
      print "Failed to load texture %s" % file
      return
    ix = image.size[0]
    iy = image.size[1]
    image = image.tostring("raw", "RGBX", 0, -1)

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
  def __init__(self, data, r):
    ACObject.__init__(self, data, r)
    glLightfv(GL_LIGHT1, GL_AMBIENT, (0.4, 0.4, 0.4, 1.0))
    glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.4, 0.4, 0.4, 1.0))
    glLightfv(GL_LIGHT1, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    glLightfv(GL_LIGHT1, GL_POSITION, self.location)
    glEnable(GL_LIGHT1)

  def render(self):
    pass


if __name__ == "__main__":
  glutInit(sys.argv)

  if (len(sys.argv) != 2):
    print "Usage: acrenderer.py <filename>"
    sys.exit(0)

  ren = ACRenderer(sys.argv[1])
  ren.run()
