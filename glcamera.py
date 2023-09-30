#! python3
# -*- coding: utf8 -*-
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import numpy as np
from numpy import linalg
from numpy import pi,sin,cos,tan


O = np.zeros(3)
X,Y,Z = np.identity(3)


class Camera:
    """Camera object.
    
    Attributes:
        parent    : stream object
        mode      : projection {0:orthogonal, 1:perspective}
        fovy_     : fov-y angle [rad]
        e2c_      : logical camera length
        h2_       : logical half height of view (h/2)
        axes[3,3] : logical base-axes (x,y,z)
        eye[3]    : logical pupil point (z)
        lpc[3]    : logical object center (o)
        depth[2]  : logical focus (near, far)
        screen[2] : screen size of viewport (w, h)
        fovy_range: fov-y angle range
    """
    ## fov = property(lambda self: self.__parent.size)
    ## fovr = property(lambda self: self.fov[0] / self.fov[1])
    ## fovx = property(lambda self: 2*arctan(self.fovr * tan(self.fovy_/2)))
    ## fovy = property(lambda self: self.fovy_)
    
    h2_ = property(lambda self: self.e2c_ * tan(self.fovy_/2))
    ## w2_ = property(lambda self: self.h2_ * self.fovr)
    
    dpu = property(lambda self: self.screen[1] / 2 / self.h2_)
    
    def __init__(self, parent):
        self.__parent = parent
        self.mode = True
        self.fovy_ = 0.1 * pi
        self.e2c_ = 30.0
        self.lpc = O
        self.eye = Z * self.e2c_
        self.axes = [X, Y, Z]
        self.depth = [0.1, 100.0]
        self.screen = [200, 200]
        self.fovy_range = (0.1*pi, 0.9*pi)
    
    def set_axes(self, z=Z, y=Y, center=O):
        self.lpc = center
        self.eye = self.lpc + z * self.e2c_
        self.axes[2] = z
        self.axes[1] = y
        self.axes[0] = np.cross(y, z)
    
    def set_view(self, w, h):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        self.screen = [w, h]
        d = self.depth
        r = w / h
        if self.mode:
            f = self.fovy_ * 180 / pi
            gluPerspective(f, r, d[0], d[1]) # range z[+,++]
        else:
            h = self.h2_
            w = h * r
            glOrtho(-w, w, -h, h, -d[1], d[1]) # range z[-,+]
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        y = self.axes[1]
        e = self.eye
        c = self.lpc
        gluLookAt(e[0], e[1], e[2], c[0], c[1], c[2], y[0], y[1], y[2])
    
    def rotate(self, dx, dy):
        """Rotate camera pupil point."""
        x, y = self.axes[0:2]
        v = (self.eye - self.lpc) + (x * dx + y * dy)
        z = v / linalg.norm(v)
        self.eye = self.lpc + z * self.e2c_
        self.axes[0] = x = np.cross(y, z)
        self.axes[1] = y = np.cross(z, x)
        self.axes[2] = z
        return True
    
    def shift(self, dx, dy):
        """Shift camera pupil point."""
        x, y = self.axes[0:2]
        v = (self.eye - self.lpc) - (x * dx + y * dy)
        z = v / linalg.norm(v)
        self.lpc = self.eye - z * self.e2c_
        self.axes[0] = x = np.cross(y, z)
        self.axes[1] = y = np.cross(z, x)
        self.axes[2] = z
        return True
    
    def tilt(self, dt):
        """Tilt xy-axis by dt [rad]."""
        x, y = self.axes[0:2]
        self.axes[0] =  x * cos(dt) + y * sin(dt)
        self.axes[1] = -x * sin(dt) + y * cos(dt)
        return True
    
    def zoom(self, rate):
        """Zoom camera length at rate."""
        L = self.e2c_ / rate
        if self.depth[0] < L < self.depth[1]:
            self.eye += self.axes[2] * (L - self.e2c_)
            self.e2c_ = L
            return True
    
    def magnify(self, angle):
        """Change fovy angle [rad] (perspective mode only)."""
        if not self.mode:
            return
        f = self.fovy_ + angle
        if self.fovy_range[0] < f < self.fovy_range[-1]:
            if self.zoom(f / self.fovy_): # adjust camera length
                self.fovy_ = f
                return True
