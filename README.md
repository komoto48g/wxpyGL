# wxpyGL

Python package based on OpenGL/GLUT
with wxPython shell extension library


## Getting Started

### Prerequisites

- Python 3.8 or later
    - mwxlib

### How to use

#### Standard GL/GLUT version

```python
from wxpyGL import glstream as gls
from wxpyGL import globject as glo

view = gls.basic_stream('teapot')
view.open()
view.objects += [
    glo.Teapot(shade=glo.silver),
    glo.Sphere(shade=glo.water, pos=(0,1,0), size=0.5),
]
view.run()
```

#### wxPython GL/GLUT version

```python
import wx
from wxpyGL import wxglstream as gls
from wxpyGL import globject as glo

def main(parent):
    view = gls.basic_stream(parent, name='teapot')
    view.open()
    view.objects += [
        glo.Teapot(shade=glo.silver),
        glo.Sphere(shade=glo.water, pos=(0,1,0), size=0.5),
    ]
    view.handler.debug = 4
    return view

if __name__ == "__main__":
    app = wx.App()
    frm = wx.Frame(None)
    view = main(frm)
    frm.Show()
    app.MainLoop()
```


## Authors

* Kazuya O'moto - *Initial work* -

See also the list of who participated in this project.


## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details
