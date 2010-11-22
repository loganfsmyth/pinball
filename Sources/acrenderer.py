

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

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

    self.reshapeFunc(width, height)

    self.loaders = [ACObject(dat) for dat in ACLoader(filename).objects]

  def displayFunc(self):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)	# Clear The Screen And The Depth Buffer
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -10.0)
    glRotated(45.0, 1.0, 1.0, 0.0)
    [l.render() for l in self.loaders]
    glutSwapBuffers()
    pass

  def idleFunc(self):
    self.displayFunc()

  def reshapeFunc(self, w, h):
    self.width = w
    self.height = h

    if h == 0:						# Prevent A Divide By Zero If The Window Is Too Small 
      h = 1

    glViewport(0, 0, w, h)		# Reset The Current Viewport And Perspective Transformation
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(w)/float(h), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)



  def keypressFunc(self, *args):
    if args[0] == '\033':
      glutDestroyWindow(self.window)
      sys.exit()

class ACObject:
  def __init__(self, data):
    self.location = data['loc']
    self.type = data['type']
    self.vertices = data['verts']
    self.surfaces = data['surfaces']
    self.subobjects = [ACObject(dat) for dat in data['kids']]

  def render(self):

    glTranslate(self.location[0], self.location[1], self.location[2])


    for surface in self.surfaces:
      glBegin(GL_POLYGON)
      glColor3dv(surface['material']['rgb'])
      for ref in surface['refs']:
        glVertex3dv(self.vertices[ref[0]])
        glTexCoord2d(ref[1], ref[2])
      glEnd()

    [obj.render() for obj in self.subobjects]
    glTranslate(-1*self.location[0], -1*self.location[1], -1*self.location[2])


if __name__ == "__main__":
  glutInit(sys.argv)

  if (len(sys.argv) != 2):
    print "Usage: acrenderer.py <filename>"
    sys.exit(0)

  ACRenderer(sys.argv[1])

  glutMainLoop()
