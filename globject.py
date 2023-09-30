#! python3
# -*- coding: utf8 -*-
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import copy
import numpy as np


N = np.zeros(4)
R,G,B,A = np.identity(4)

O = np.zeros(3)
X,Y,Z = np.identity(3)


class Material:
    def __init__(self, a, d, s, sh):
        self.ambient = a
        self.diffuse = d
        self.specular = s
        self.shininess = sh
    
    def __str__(self):
        return '\n'.join("  {:>12} : {}".format(k,v) for k,v in vars(self).items())
    
    def set_alpha(self, a):
        self = copy.deepcopy(self)
        self.ambient[3] = self.diffuse[3] = self.specular[3] = a
        return self


black   = Material([0, 0, 0, 1], [0, 0, 0, 1], [0, 0, 0, 1], 100)
red     = Material([1, 0, 0, 1], [1, 0, 0, 1], [1, 0, 0, 1], 100)
green   = Material([0, 1, 0, 1], [0, 1, 0, 1], [0, 1, 0, 1], 100)
blue    = Material([0, 0, 1, 1], [0, 0, 1, 1], [0, 0, 1, 1], 100)
white   = Material([1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], 100)

water   = Material([0.5,      0.5,      0.7,      0.75],
                   [0.1,      0.5,      0.8,      0.75],
                   [1.0,      1.0,      1.0,      0.75], 100.0 )

gold    = Material([0.24725,  0.1995,   0.0745,   1.0 ],
                   [0.75164,  0.60648,  0.22648,  1.0 ],
                   [0.628281, 0.555802, 0.366065, 1.0 ],  51.2 )

silver  = Material([0.19225,  0.19225,  0.19225,  1.0 ],
                   [0.50754,  0.50754,  0.50754,  1.0 ],
                   [0.508273, 0.508273, 0.508273, 1.0 ],  51.2 )

copper  = Material([0.19125,  0.0735,   0.0225,   1.0 ],
                   [0.7038,   0.27048,  0.0828,   1.0 ],
                   [0.256777, 0.137622, 0.086014, 1.0 ],  12.8 )

chrome  = Material([0.25,     0.25,     0.25,     1.0 ],
                   [0.40,     0.40,     0.40,     1.0 ],
                   [0.774597, 0.774597, 0.774597, 1.0 ],  12.8 )

bronze  = Material([0.2125,   0.1275,   0.054,    1.0 ],
                   [0.714,    0.4284,   0.18144,  1.0 ],
                   [0.393548, 0.271906, 0.166721, 1.0 ],  25.6 )

brass   = Material([0.329412, 0.223529, 0.027451, 1.0 ],
                   [0.780392, 0.568627, 0.113725, 1.0 ],
                   [0.992157, 0.941176, 0.807843, 1.0 ],  27.9 )

emerald = Material([0.0215,   0.1745,   0.0215,   1.0 ],
                   [0.07568,  0.61424,  0.07568,  1.0 ],
                   [0.633,    0.727811, 0.633,    1.0 ],  76.8 )

jade    = Material([0.135,    0.2225,   0.1575,   1.0 ],
                   [0.54,     0.89,     0.63,     1.0 ],
                   [0.316228, 0.316228, 0.316228, 1.0 ],  12.8 )

obsidian= Material([0.05375,  0.05,     0.06625,  1.0 ],
                   [0.18275,  0.17,     0.22525,  1.0 ],
                   [0.332741, 0.328634, 0.346435, 1.0 ],  38.4 )

turk    = Material([0.1,      0.18725,  0.1745,   1.0 ],
                   [0.396,    0.74151,  0.69102,  1.0 ],
                   [0.297254, 0.30829,  0.306678, 1.0 ],  12.8 )

pearl   = Material([0.25,     0.20725,  0.20725,  1.0 ],
                   [1.0,      0.829,    0.829,    1.0 ],
                   [0.296648, 0.296648, 0.296648, 1.0 ],  10.24)

ruby    = Material([0.1745,   0.01175,  0.01175,  1.0 ],
                   [0.61424,  0.04136,  0.04136,  1.0 ],
                   [0.727811, 0.626959, 0.626959, 1.0 ],  76.8 )


class Object:
    """Object base class.
    
    Note:
        Users should override the following functions:
        - draw_dots(self) <- MDOT
        - draw_line(self) <- MWIRE
        - draw_face(self) <- MSOLID
    """
    ## Mesh frame_style
    MDOT   = 0x0001
    MWIRE  = 0x0002
    MSOLID = 0x0004
    
    ## Mesh color_style
    MRGBA  = 0x0010
    MSHADE = 0x0020
    MALPHA = 0x0040
    
    def __init__(self, pos=None, shade=None, style=None, visible=True):
        if pos is None:
            pos = O
        self.pos = pos
        self.shade = shade or white
        self.style = style or self.MWIRE | self.MSOLID | self.MSHADE
        self.visible = visible
    
    def __call__(self):
        if not self.visible:
            return
        
        ## set palette type
        if self.style & self.MRGBA:
            glEnable(GL_COLOR_MATERIAL)
            glColor4dv(self.shade)
        
        elif self.style & self.MSHADE:
            glDisable(GL_COLOR_MATERIAL)
            glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, self.shade.ambient)
            glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, self.shade.diffuse)
            glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, self.shade.specular)
            glMaterialf (GL_FRONT_AND_BACK, GL_SHININESS, self.shade.shininess)
        
        ## begin blend
        if self.style & self.MALPHA:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        try:
            glPushMatrix()
            glTranslated(*self.pos)
            
            if self.style & self.MDOT:
                glDepthMask(False)
                self.draw_dots()
            
            if self.style & self.MWIRE:
                glDepthMask(False)
                self.draw_line()
            
            if self.style & self.MSOLID:
                glDepthMask(True)
                self.draw_face()
        finally:
            glPopMatrix()
        
        ## end blend
        if self.style & self.MALPHA:
            glDisable(GL_BLEND)
    
    def draw_dots(self):
        pass
    
    def draw_line(self):
        pass
    
    def draw_face(self):
        pass

## --------------------------------
## Standard glut models
## --------------------------------

class Sphere(Object):
    def __init__(self, size=1, **kwargs):
        super().__init__(**kwargs)
        self.size = size
    
    def draw_line(self):
        glutWireSphere(self.size, 36, 18)
    
    def draw_face(self):
        glutSolidSphere(self.size, 36, 18)


class Teapot(Object):
    def __init__(self, size=1, **kwargs):
        super().__init__(**kwargs)
        self.size = size
    
    def draw_line(self):
        glFrontFace(GL_CW)
        glutWireTeapot(self.size)
        glFrontFace(GL_CCW)
    
    def draw_face(self):
        glFrontFace(GL_CW)
        glutSolidTeapot(self.size)
        glFrontFace(GL_CCW)
