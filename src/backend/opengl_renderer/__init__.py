'''
Offscreen rendering using GLUT hidden window
Standalone code - not using LibGL from this repository
'''
import OpenGL
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import imageio.v3 as imageio

import numpy as np
import sys

width, height = 300, 300

class Cube():
    def __init__(self):
        self.verticies = (
            (1, -1, -1),
            (1, 1, -1),
            (-1, 1, -1),
            (-1, -1, -1),
            (1, -1, 1),
            (1, 1, 1),
            (-1, -1, 1),
            (-1, 1, 1)
            )

        self.edges = (
            (0,1),
            (0,3),
            (0,4),
            (2,1),
            (2,3),
            (2,7),
            (6,3),
            (6,4),
            (6,7),
            (5,1),
            (5,4),
            (5,7)
            )
    
    def render(self):
        glEnable(GL_LINE_SMOOTH)
        glLineWidth(4)
        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.verticies[vertex])
        glEnd()
    
class OpenGL_renderer():
    def __init__(self):
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
        glutInitWindowSize(width, height)
        glutCreateWindow(b"OpenGL Offscreen")
        glutHideWindow()
        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)
    
        glClearColor(0.5, 0.5, 0.5, 1.0)
        glColor(0.0, 1.0, 0.0)
        gluPerspective(45, (width/height), 0.1, 50.0)

        glTranslatef(0.0,0.0, -5)
        glViewport(0, 0, width, height)

        self.contents = []
        self.contents.append(Cube())

    def render(self):

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        for item in self.contents:
            item.render()

        glFlush()
        glPixelStorei(GL_PACK_ALIGNMENT, 1)

        render = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
        render = np.frombuffer(render, dtype=np.uint8).reshape(width, height, 4)

        depth = glReadPixels(0, 0, width, height, GL_DEPTH_COMPONENT, GL_FLOAT)
        depth = np.frombuffer(depth, dtype=np.float32).reshape(width, height)
                
        glutSwapBuffers()
        return render, depth
    
if __name__ == "__main__":
    a = OpenGL_renderer()
    a.render()