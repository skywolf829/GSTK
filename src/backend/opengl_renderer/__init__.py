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
verticies = (
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, -1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, -1, 1),
    (-1, 1, 1)
    )

edges = (
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

def init():
    glClearColor(0.5, 0.5, 0.5, 1.0)
    glColor(0.0, 1.0, 0.0)
    gluPerspective(45, (width/height), 0.1, 50.0)

    glTranslatef(0.0,0.0, -5)
    glViewport(0, 0, width, height)

def render():

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_LINE_SMOOTH)
    glLineWidth(4)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(verticies[vertex])
    glEnd()

    glFlush()


def draw():
    render()
    #glutSwapBuffers()
    


def main():
    glutInit(sys.argv)

    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(width, height)
    glutCreateWindow(b"OpenGL Offscreen")
    glutHideWindow()
    glEnable(GL_DEPTH_TEST)
    glDepthMask(GL_TRUE)

    init()
    draw()

    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
    data = np.frombuffer(data, dtype=np.uint8).reshape(width, height, 4)
    print(data.shape)
    imageio.imwrite("glut.png", data)

    data2 = glReadPixels(0, 0, width, height, GL_DEPTH_COMPONENT, GL_FLOAT)
    data2 = np.frombuffer(data2, dtype=np.float32).reshape(width, height)[...,None].repeat(4, 2)
    data2 -= data2.min()
    data2 /= data2.max()
    data2 *= 255
    data2 = data2.astype(np.uint8)
    imageio.imwrite("glut_depth.png", data2)

    #glutDisplayFunc(draw)
    #glutMainLoop()

if __name__ == "__main__":
    main()