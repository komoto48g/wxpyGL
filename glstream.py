#! python3
# -*- coding: utf8 -*-
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
## from OpenGL.GLUT.freeglut import *

from mwx import FSM
from .glcamera import Camera


speckeys = dict(enumerate('abcdefghijklmnopqrstuvwxyz', 1)) # C-[a-z]

speckeys.update({ # Other control chars
    #  8 : 'backspace', # [C-h]
    #  9 : 'tab',       # [C-i]
    # 13 : 'enter',     # [C-m]
    0xba : ':',
    0xbb : ';',     0x1b : '[',     0xdb : '{',
    0xbc : ',',     0x1c : '\\',    0xdc : '|',
    0xbd : '-',     0x1d : ']',     0xdd : '}',
    0xbe : '.',     0x1e : '^',     0xde : '~',
    0xbf : '/',     0x1f : '-',
    0xc0 : '@',
    0xe2 : '_',
})

glut_speckeys = { #<class 'OpenGL.constant.IntConstant'>
    GLUT_KEY_F1         : 'f1',
    GLUT_KEY_F2         : 'f2',
    GLUT_KEY_F3         : 'f3',
    GLUT_KEY_F4         : 'f4',
    GLUT_KEY_F5         : 'f5',
    GLUT_KEY_F6         : 'f6',
    GLUT_KEY_F7         : 'f7',
    GLUT_KEY_F8         : 'f8',
    GLUT_KEY_F9         : 'f9',
    GLUT_KEY_F10        : 'f10',
    GLUT_KEY_F11        : 'f11',
    GLUT_KEY_F12        : 'f12',
    GLUT_KEY_DOWN       : 'down',
    GLUT_KEY_END        : 'end',
    GLUT_KEY_HOME       : 'home',
    GLUT_KEY_INSERT     : 'insert',
    GLUT_KEY_LEFT       : 'left',
    GLUT_KEY_PAGE_DOWN  : 'pagedown',
    GLUT_KEY_PAGE_UP    : 'pageup',
    GLUT_KEY_RIGHT      : 'right',
    GLUT_KEY_UP         : 'up',
    0x70 : 'shift',     # GLUT_KEY_SHIFT (112)
    0x72 : 'ctrl',      # GLUT_KEY_CTRL  (114)
    0x74 : 'alt',       # GLUT_KEY_ALT   (116)
}

def get_hotkey(key):
    try:
        code = ord(key)
        key = speckeys.get(code) or key.decode().lower()
        states = glutGetModifiers()
        mod = ""
        if states & GLUT_ACTIVE_CTRL:  mod += 'C-' # 2
        if states & GLUT_ACTIVE_ALT:   mod += 'M-' # 4
        if states & GLUT_ACTIVE_SHIFT: mod += 'S-' # 1
        return mod + key
    except UnicodeDecodeError:
        print("- unknown code {!r}".format(code))
        pass

def get_speckey(code):
    try:
        key = glut_speckeys.get(code)
        states = glutGetModifiers()
        mod = ""
        if key != 'ctrl'  and states & GLUT_ACTIVE_CTRL:  mod += 'C-' # 2
        if key != 'alt'   and states & GLUT_ACTIVE_ALT:   mod += 'M-' # 4
        if key != 'shift' and states & GLUT_ACTIVE_SHIFT: mod += 'S-' # 1
        return mod + key
    except Exception:
        print("- unknown code {!r}".format(code))
        pass

def regulate_key(key):
    return (key.replace("ctrl+",  "C-") # modifier keys abbreviation
               .replace("alt+",   "M-")
               .replace("shift+", "S-")
               .replace("win+", "win-")
               .replace("M-C-", "C-M-") # modifier key regulation C-M-S-
               .replace("S-M-", "M-S-")
               .replace("S-C-", "C-S-"))


class basic_stream:
    """The basic stream
    
    Attributes:
        name    : window title
        pos[2]  : window position (x, y)
        size[2] : window size (width, height)
        color[4]: back color
        camera  : singlet camera model
        dpu     : dot per logical length
    """
    dpu = property(lambda self: self.size[1] / 2 / self.camera.h2_)
    
    def __init__(self):
        glutInit(sys.argv)
        
        self.__key = ''
        self.__button = ''
        self.__oblist = []
        
        self.handler = FSM({
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
            default = 0,
        )
    
    def open(self, name, size=None, pos=None, color=None):
        self.name = name.encode() #<class 'bytes'>
        self.pos = pos or (0, 0)
        self.size = size or (300, 300)
        self.color = color or (0, 0, 0, 0)
        
        glutInitWindowSize(*self.size)
        glutInitWindowPosition(*self.pos)
        
        ## Set context here (single or double buffer, depthtest, etc.)
        
        ## glutInitDisplayMode(GLUT_RGBA | GLUT_SINGLE)
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        
        glutCreateWindow(self.name)
        glClearColor(*self.color)
        
        self.camera = Camera(self)
        
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
        ## glShadeModel(GL_FLAT)
        
        ## hints
        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        glHint(GL_FOG_HINT, GL_NICEST)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
        
        ## glut connect funcs
        glutDisplayFunc(self.on_display)
        glutReshapeFunc(self.on_reshape)
        glutKeyboardFunc(self.on_key_press)
        glutKeyboardUpFunc(self.on_key_release)
        glutSpecialFunc(self.on_specialkey_press)
        glutSpecialUpFunc(self.on_specialkey_release)
        glutMouseFunc(self.on_mouse)
        glutMotionFunc(self.on_motion)
        glutVisibilityFunc(self.on_visible)
        glutWMCloseFunc(self.close)
        glutIdleFunc(None)
        
        return self
    
    def add_objects(self, obj):
        self.__oblist += list(obj)
    
    def run(self):
        glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE,
                      ## GLUT_ACTION_CONTINUE_EXECUTION,
                      GLUT_ACTION_GLUTMAINLOOP_RETURNS,
                      )
        glutMainLoop()
    
    def close(self):
        glutLeaveMainLoop()
    
    ## --------------------------------
    ## glut actions
    ## --------------------------------
    
    def on_display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        w, h = self.size
        if w and h:
            self.camera.set_view(w, h)
            for p in self.__oblist: # draw all objects
                p()
            glutSwapBuffers()
    
    def on_reshape(self, w, h):
        self.size = (w, h)
        glViewport(0, 0, w, h) # --> single viewport region
    
    def on_key_press(self, key, x, y):
        key = get_hotkey(key)
        self.__key = regulate_key(key + '+')
        self.handler('{} pressed'.format(key), x, y)
    
    def on_key_release(self, key, x, y):
        key = get_hotkey(key)
        self.__key = ''
        self.handler('{} released'.format(key), x, y)
    
    def on_specialkey_press(self, code, x, y):
        key = get_speckey(code)
        self.__key = regulate_key(key + '+')
        self.handler('{} pressed'.format(key), x, y)
    
    def on_specialkey_release(self, code, x, y):
        key = get_speckey(code)
        self.__key = ''
        self.handler('{} released'.format(key), x, y)
    
    def on_mouse(self, button, state, x, y):
        if button >= 3: # wheel
            if state == GLUT_DOWN:
                p = 'up' if button == 3 else 'down'
                self.handler('{}wheel{} pressed'.format(self.__key, p), x, y)
            return
        
        btn = self.__key + "LMR"[button] # {0:L,1:M,2:R}
        if state == GLUT_DOWN:
            self.__button = btn
            self.handler('{}button pressed'.format(btn), x, y)
        else:
            self.__button = ''
            self.handler('{}button released'.format(btn), x, y)
    
    def on_motion(self, x, y):
        if self.__button:
            self.handler('{}drag move'.format(self.__button), x, y)
    
    def on_visible(self, state):
        if state:
            self.handler('window_shown')
        else:
            self.handler('window_hidden')
    
    ## --------------------------------
    ## Mouse / Keyboard interface
    ## --------------------------------
    
    def OnHomePosition(self, x, y):
        self.camera.set_axes()
        glutPostRedisplay()
    
    def OnDragBegin(self, x, y):
        self._lx = x
        self._ly = y
        self.lcx = self.size[0] / 2
        self.lcy = self.size[1] / 2
        self.lvx = x - self.lcx
        self.lvy = self.lcy - y
    
    def OnDragMove(self, x, y):
        d = self.dpu / 4
        self.camera.rotate(-(x-self._lx)/d, (y-self._ly)/d)
        self._lx = x
        self._ly = y
        glutPostRedisplay()
    
    def OnDragEnd(self, x, y):
        glutPostRedisplay()
    
    def OnShiftMove(self, x, y):
        d = self.dpu
        self.camera.shift(-(x-self._lx)/d, (y-self._ly)/d)
        self._lx = x
        self._ly = y
        glutPostRedisplay()
    
    def OnTiltMove(self, x, y):
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
        glutPostRedisplay()
    
    def OnZoomView(self, x, y):
        ds = (x-self._lx + self._ly-y) / 100 # zoom
        self.camera.zoom(1 + ds)
        self._lx = x
        self._ly = y
        glutPostRedisplay()
    
    def OnZoomFovy(self, x, y):
        ds = (x-self._lx + self._ly-y) / 100 # angle
        self.camera.magnify(ds)
        self._lx = x
        self._ly = y
        glutPostRedisplay()
    
    def OnScrollZoomUp(self, x, y):
        self.camera.zoom(1.25)
        glutPostRedisplay()
    
    def OnScrollZoomDown(self, x, y):
        self.camera.zoom(1/1.25)
        glutPostRedisplay()
