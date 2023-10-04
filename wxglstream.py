#! python3
# -*- coding: utf8 -*-
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import wx
from wx.glcanvas import GLCanvas, GLContext

from mwx.framework import CtrlInterface
from .glcamera import Camera


class basic_stream(GLCanvas, CtrlInterface):
    """The basic stream
    
    Attributes:
        name    : window title
        camera  : singlet camera model
        objects : list <Object> to draw
    """
    @property
    def dpu(self):
        """Dots per unit:logical length."""
        return self._size[1] / 2 / self.camera.h2_
    
    def __init__(self, *args, **kwargs):
        self._size = kwargs.setdefault('size', (300, 300))
        GLCanvas.__init__(self, *args, **kwargs)
        CtrlInterface.__init__(self)
        
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        
        self.context = GLContext(self)
        self.camera = Camera(self)
        self.objects = []
        
        self.handler.update({ # DNA<basic_stream>
                0 : {
                 'home pressed' : (0, self.OnHomePosition),
             '*Lbutton pressed' : (1, self.OnDragBegin),
             '*Rbutton pressed' : (2, self.OnDragBegin),
            'C-wheelup pressed' : (0, self.OnScrollZoomUp),
          'C-wheeldown pressed' : (0, self.OnScrollZoomDown),
                },
                1 : {
                   'Ldrag move' : (1, self.OnDragMove),
                 'M-Ldrag move' : (1, self.OnTiltMove),
                 'S-Ldrag move' : (1, self.OnShiftMove),
                 'C-Ldrag move' : (1, self.OnZoomView),
            '*Lbutton released' : (0, self.OnDragEnd),
                },
                2 : {
                 'C-Rdrag move' : (2, self.OnZoomFovy),
            '*Rbutton released' : (0, self.OnDragEnd),
                },
            },
        )
        
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        
        def _release(evt):
            if self.HasCapture():
                self.ReleaseMouse()
            evt.Skip()
        self.Bind(wx.EVT_LEFT_UP, _release)
        self.Bind(wx.EVT_RIGHT_UP, _release)
        
        def _capture(evt):
            _release(evt)
            self.SetFocus() # required to get key events
            self.CaptureMouse()
            evt.Skip()
        self.Bind(wx.EVT_LEFT_DOWN, _capture)
        self.Bind(wx.EVT_RIGHT_DOWN, _capture)
    
    def open(self):
        """Open stream.
        Set context here (double-buffer, depth-test, etc.).
        """
        self.SetCurrent(self.context)
        
        ## culling
        glCullFace(GL_BACK)
        glEnable(GL_CULL_FACE)
        
        ## depth test
        glEnable(GL_DEPTH_TEST)
        
        ## standard environ light
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)
        
        ## initialize GL context
        glRenderMode(GL_RENDER)
        glShadeModel(GL_SMOOTH)
        
        ## hints
        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        glHint(GL_FOG_HINT, GL_NICEST)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
    
    def draw(self):
        self.Refresh()
    
    def OnSize(self, evt):
        def reshape():
            w, h = self.ClientSize
            self._size = w, h
            glViewport(0, 0, w, h) # --> single viewport region
        wx.CallAfter(reshape)
        evt.Skip()
    
    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        self.SetCurrent(self.context)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        w, h = self._size
        if w and h:
            self.camera.set_view(w, h)
            for obj in self.objects: # draw objects
                obj()
            self.SwapBuffers()
        evt.Skip()
    
    ## --------------------------------
    ## Mouse / Keyboard interface
    ## --------------------------------
    
    def OnHomePosition(self, evt):
        self.camera.set_axes()
        self.draw()
    
    def OnDragBegin(self, evt):
        x, y = evt.x, evt.y
        self._lx = x
        self._ly = y
        self.lcx = self._size[0] / 2
        self.lcy = self._size[1] / 2
        self.lvx = x - self.lcx
        self.lvy = self.lcy - y
    
    def OnDragMove(self, evt):
        x, y = evt.x, evt.y
        d = self.dpu / 4
        self.camera.rotate(-(x-self._lx)/d, (y-self._ly)/d)
        self._lx = x
        self._ly = y
        self.draw()
    
    def OnDragEnd(self, evt):
        self.draw()
    
    def OnShiftMove(self, evt):
        x, y = evt.x, evt.y
        d = self.dpu
        self.camera.shift(-(x-self._lx)/d, (y-self._ly)/d)
        self._lx = x
        self._ly = y
        self.draw()
    
    def OnTiltMove(self, evt):
        x, y = evt.x, evt.y
        vx = x - self.lcx
        vy = self.lcy - y
        vv = vx*vx + vy*vy
        if vv < 10:
            return # prevent zero-division
        
        self.camera.tilt((vx * self.lvy - vy * self.lvx) / vv)
        self._lx = x
        self._ly = y
        self.lvx = vx
        self.lvy = vy
        self.draw()
    
    def OnZoomView(self, evt):
        x, y = evt.x, evt.y
        ds = (x-self._lx + self._ly-y) / 100 # zoom
        self.camera.zoom(1 + ds)
        self._lx = x
        self._ly = y
        self.draw()
    
    def OnZoomFovy(self, evt):
        x, y = evt.x, evt.y
        ds = (x-self._lx + self._ly-y) / 100 # angle
        self.camera.magnify(ds)
        self._lx = x
        self._ly = y
        self.draw()
    
    def OnScrollZoomUp(self, evt):
        self.camera.zoom(1.25)
        self.draw()
    
    def OnScrollZoomDown(self, evt):
        self.camera.zoom(1/1.25)
        self.draw()
