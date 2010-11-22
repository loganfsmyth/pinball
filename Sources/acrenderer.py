

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from acloader import *

class ACRenderer:
  def __init__(self, filename, width = 800, height = 600):

#    self.width = width
#    self.height = height

    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    glutInitWindowSize(width, height)
    glutInitWindowPosition(100, 100)
    self.window = glutCreateWindow("ACRenderer")

    glutDisplayFunc(self.displayFunc)
    glutIdleFunc(self.idleFunc)
    glutReshapeFunc(self.reshapeFunc)
    glutKeyboardFunc(self.keypressFunc)

    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)

#    glMatrixMode(GL_PROJECTION)
#    glLoadIdentity()
#    gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)
#    glMatrixMode(GL_MODELVIEW)
    self.reshapeFunc(width, height)


  def displayFunc(self):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);	# Clear The Screen And The Depth Buffer
    glLoadIdentity();					# Reset The View
    glTranslatef(-1.5,0.0,-6.0)				# Move Left And Into The Screen



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

if __name__ == "__main__":
  glutInit(sys.argv)

  if (len(sys.argv) != 2):
    print "Usage: acrenderer.py <filename>"
    sys.exit(0)

  ACRenderer(sys.argv[1])

  glutMainLoop()
