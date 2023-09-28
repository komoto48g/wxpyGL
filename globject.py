#! python3
# -*- coding: utf8 -*-
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
## from OpenGL.GLUT.freeglut import *

import numpy as np
from numpy import pi

from .glmaterial import white


N = np.zeros(4)
R,G,B,A = np.identity(4)

O = np.zeros(3)
X,Y,Z = np.identity(3)


class Object(object):
    """Object base class
    
    Note: Users should override the following functions:
          draw_dots(self) <- MDOT
          draw_line(self) <- MWIRE
          draw_face(self) <- MSOLID
    """
    ## Mesh frame_style
    MDOT   = 0x0001
    MWIRE  = 0x0002
    MSOLID = 0x0004
    
    ## Mesh color_style
    MRGBA  = 0x0010
    MSHADE = 0x0020
    MALPHA = 0x0040
    
    def __init__(self, parent, pos=None, shade=None, style=None, visible=True):
        self.__parent = parent
        if pos is None:
            pos = O
        self.pos = pos
        self.shade = shade or white
        self.style = style or Object.MWIRE | Object.MSOLID | Object.MSHADE
        self.visible = visible
    
    def __call__(self):
        if not self.visible:
            return
        
        ## set palette type
        if self.style & Object.MRGBA:
            glEnable(GL_COLOR_MATERIAL)
            glColor4dv(self.shade)
        
        elif self.style & Object.MSHADE:
            glDisable(GL_COLOR_MATERIAL)
            glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, self.shade.ambient)
            glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, self.shade.diffuse)
            glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, self.shade.specular)
            glMaterialf (GL_FRONT_AND_BACK, GL_SHININESS, self.shade.shininess)
        
        ## begin blend
        if self.style & Object.MALPHA:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        try:
            glPushMatrix()
            glTranslated(*self.pos)
            
            if self.style & Object.MDOT:
                glDepthMask(False)
                self.draw_dots()
            
            if self.style & Object.MWIRE:
                glDepthMask(False)
                self.draw_line()
            
            if self.style & Object.MSOLID:
                glDepthMask(True)
                self.draw_face()
        finally:
            glPopMatrix()
        
        ## end blend
        if self.style & Object.MALPHA:
            glDisable(GL_BLEND)
    
    def draw_dots(self):
        pass
    
    def draw_line(self):
        pass
    
    def draw_face(self):
        pass

## --------------------------------
## Standard models
## --------------------------------

class Sphere(Object):
    def __init__(self, parent, size=1, **kwargs):
        Object.__init__(self, parent, **kwargs)
        self.size = size
    
    def draw_line(self):
        glutWireSphere(self.size, 36, 18)
    
    def draw_face(self):
        glutSolidSphere(self.size, 36, 18)


class Teapot(Object):
    def __init__(self, parent, size=1, **kwargs):
        Object.__init__(self, parent, **kwargs)
        self.size = size
    
    def draw_line(self):
        glFrontFace(GL_CW)
        glutWireTeapot(self.size)
        glFrontFace(GL_CCW)
    
    def draw_face(self):
        glFrontFace(GL_CW)
        glutSolidTeapot(self.size)
        glFrontFace(GL_CCW)
