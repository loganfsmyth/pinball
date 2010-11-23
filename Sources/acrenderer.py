

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import Image

from acloader import *



class ACRenderer:
  def __init__(self, filename, width = 800, height = 600):

    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    glutInitWindowSize(width, height)
    glutInitWindowPosition(100, 100)
    self.window = glutCreateWindow("ACRenderer")

    glutDisplayFunc(self.displayFunc)
#    glutIdleFunc(self.idleFunc)
    glutReshapeFunc(self.reshapeFunc)
    glutKeyboardFunc(self.keypressFunc)

    glClearColor(0.5, 0.5, 0.5, 0.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_TEXTURE_2D)

    self.reshapeFunc(width, height)

    print "Loading %s" % filename
    self.loaders = [ACObject(dat) for dat in ACLoader(filename).objects]
    print "Completed loading"

  def displayFunc(self):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)	# Clear The Screen And The Depth Buffer
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -3.0)
    glRotated(45.0, 1.0, 0.0, 0.0)

    [l.render() for l in self.loaders]
    glutSwapBuffers()
    pass

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



  def keypressFunc(self, *args):
    if args[0] == '\033': # Escape key
      glutDestroyWindow(self.window)
      sys.exit()

class ACObject:
  def __init__(self, data):
    self.location = data['loc']
    self.type = data['type']
    self.vertices = data['verts']
    self.texture = 0
    if data.has_key('texture'):
      self.__loadTexture(data['texture'])
    self.texfile =  data.has_key('texture') and data['texture'] or ''

    self.surfaces = data['surfaces']
    self.subobjects = [ACObject(dat) for dat in data['kids']]

  def render(self):
    glTranslate(self.location[0], self.location[1], self.location[2])

    glBindTexture(GL_TEXTURE_2D, self.texture)

    for surface in self.surfaces:
      glBegin(GL_POLYGON)
      glColor3dv(surface['material']['rgb'])
      for ref in surface['refs']:
        glTexCoord2d(ref[1], ref[2])
        glVertex3dv(self.vertices[ref[0]])
      glEnd()

    [obj.render() for obj in self.subobjects]
    glTranslate(-1*self.location[0], -1*self.location[1], -1*self.location[2])

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



if __name__ == "__main__":
  glutInit(sys.argv)

  if (len(sys.argv) != 2):
    print "Usage: acrenderer.py <filename>"
    sys.exit(0)

  ACRenderer(sys.argv[1])

  glutMainLoop()
