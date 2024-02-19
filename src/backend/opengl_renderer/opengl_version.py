'''
Offscreen rendering using GLUT hidden window
Standalone code - not using LibGL from this repository
'''
import OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
import glfw


import imageio.v3 as imageio

import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from dataset.cameras import RenderCam
from tqdm import tqdm

# https://gist.github.com/leon-nn/cd4e3d50eb0fa23d8e197102f49f2cb3
class Cube():
    def __init__(self, 
                 T = np.zeros(3, dtype=np.float32), 
                 R = np.eye(3, dtype=np.float32),
                 color = np.array([0.0, 1.0, 0.0], dtype=np.float32)):
        
        self.verticies = np.array([
            (1, -1, -1),
            (1, 1, -1),
            (-1, 1, -1),
            (-1, -1, -1),
            (1, -1, 1),
            (1, 1, 1),
            (-1, -1, 1),
            (-1, 1, 1)], dtype=np.float32
            )

        self.edges = np.array([
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
            (5,7)], dtype=np.uint8
            )
    
        self.color = color
        self.T = T
        self.R = R

    def render(self):
        glEnable(GL_LINE_SMOOTH)
        glLineWidth(4)
        glColor(self.color[0],
                self.color[1],
                self.color[2])
        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                v = self.R @ self.verticies[vertex][:,None]
                v = v[:,0] + self.T
                glVertex3fv(v)
        glEnd()
    
    

class OpenGL_renderer():
    def __init__(self):
        
        self.framebufferObject = None
        self.last_texture_size = [0,0]
        self.window = None

        self.init_openGL()
        
        self.contents = []

    def add_item(self, item):
        self.contents.append(item)

    def remove_item(self, item):
        self.contents.remove(item)

    def init_openGL(self):

        if not glfw.init():
            print("Failed to start glfw - exiting")
            quit()

        # Create a windowed mode window and its OpenGL context
        glfw.window_hint(glfw.VISIBLE, False)
        self.window = glfw.create_window(100, 100, "Hello World", None, None)

        if not self.window:
            print("Failed to create window - exiting")
            glfw.terminate()
            quit()

        # Make the window's context current
        glfw.make_context_current(self.window)
        #glfw.swap_interval(100)

        # Performs face culling
        #glEnable(GL_CULL_FACE)
        #glCullFace(GL_BACK)
        #glFrontFace(GL_CW)
        
        # Performs z-buffer testing
        glEnable(GL_DEPTH_TEST)
        #glDepthMask(GL_TRUE)
        #glDepthFunc(GL_LEQUAL)
        #glDepthRange(0.0, 1.0)
       
    def init_FBO(self, w, h):
        if(w == self.last_texture_size[0] and \
           h == self.last_texture_size[1]):
            return
        
        # Create a handle and assign a texture buffer to it
        self.renderedTexture = glGenTextures(1)
        # Bind the texture buffer to the GL_TEXTURE_2D target in the 
        # OpenGL context
        glBindTexture(GL_TEXTURE_2D, self.renderedTexture)
        # Attach a texture 'img' (which should be of unsigned bytes) 
        # to the texture buffer. If you don't want a specific 
        # texture, you can just replace 'img' with 'None'.
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 
                     w, h, 0, GL_RGB,
                     GL_UNSIGNED_BYTE, None)
        # Does some filtering on the texture in the texture buffer
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        # Unbind the texture buffer from the GL_TEXTURE_2D target in the OpenGL context
        glBindTexture(GL_TEXTURE_2D, 0)

        # Create a handle and assign a renderbuffer to it
        depthRenderbuffer = glGenRenderbuffers(1)
        # Bind the renderbuffer to the GL_RENDERBUFFER target in the OpenGL context
        glBindRenderbuffer(GL_RENDERBUFFER, depthRenderbuffer)
        # Allocate enough memory for the renderbuffer to hold 
        # depth values for the texture
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, 
                            w, h)
        # Unbind the renderbuffer from the GL_RENDERBUFFER 
        # target in the OpenGL context
        glBindRenderbuffer(GL_RENDERBUFFER, 0)

        # Create a handle and assign the FBO to it
        self.framebufferObject = glGenFramebuffers(1)
        # Use our initialized FBO instead of the default GLUT framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, self.framebufferObject)
        # Attaches the texture buffer created above to the 
        # GL_COLOR_ATTACHMENT0 attachment point of the FBO
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.renderedTexture, 0)
        # Attaches the renderbuffer created above to the 
        # GL_DEPTH_ATTACHMENT attachment point of the FBO
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depthRenderbuffer)

        # Sees if your GPU can handle the FBO configuration defined above
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError('Framebuffer binding failed, probably because your GPU does not support this FBO configuration.')

        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)

        # Unbind the FBO, relinquishing the GL_FRAMEBUFFER back to the window manager (i.e. GLUT)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        self.last_texture_size = [w,h]

    def reset_FBO(self):
        """
        Clears the color and depth in the FBO
        """
        # Clears any color or depth information in the FBO
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClearDepth(1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
    def render(self, render_cam : RenderCam):
        #glfw.make_context_current(self.window)
        
        self.init_FBO(render_cam.image_width,
                    render_cam.image_height)
        
        # Bind FBO for render
        glBindFramebuffer(GL_FRAMEBUFFER, self.framebufferObject)
        
        # Clear FBO for new draw       
        self.reset_FBO()
        

        # Reset viewport location
        glViewport(0, 0, render_cam.image_width,
                render_cam.image_height)
        # Update projection matrix
        glMatrixMode(GL_PROJECTION)
        #glLoadIdentity()
        #gluPerspective(np.rad2deg(render_cam.FoVx), 
        #               render_cam.image_width/render_cam.image_height, 
        #               render_cam.znear, render_cam.zfar)
        glLoadMatrixf(render_cam.projection_matrix.cpu().numpy())
        glMatrixMode(GL_MODELVIEW)
        #glLoadIdentity()
        glLoadMatrixf(render_cam.world_view_transform.cpu().numpy())
        
        for item in self.contents:
            item.render()
        glFlush()
        
        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        glReadBuffer(GL_COLOR_ATTACHMENT0)

        render = glReadPixels(0, 0, render_cam.image_width,
                            render_cam.image_height, 
                            GL_RGBA, GL_UNSIGNED_BYTE)
        render = np.frombuffer(render, dtype=np.uint8).reshape(
            render_cam.image_width, render_cam.image_height, 4)

        depth = glReadPixels(0, 0, render_cam.image_width,
                            render_cam.image_height,
                            GL_DEPTH_COMPONENT, GL_FLOAT)
        depth = np.frombuffer(depth, dtype=np.float32).reshape(
            render_cam.image_width, render_cam.image_height)
        
        
        #render = np.empty([render_cam.image_width, render_cam.image_height, 4], dtype=np.uint8)
        #depth = np.empty([render_cam.image_width, render_cam.image_height], dtype=np.float32)
        # Unbind cleanup
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        
        #glutSwapBuffers()
        return render, depth
    
if __name__ == "__main__":
    a = OpenGL_renderer()
    cam = RenderCam(znear = 0.1, zfar=4000)
    a.add_item(Cube())
    
    import torch
    for _ in tqdm(range(10000)):
        render, depth = a.render(cam)
        r = torch.tensor(render, device="cuda", dtype=torch.uint8)
        d = torch.tensor(depth, device="cuda", dtype=torch.float32)
        torch.cuda.synchronize()





