# wxpyGL

Python package based on OpenGL/GLUT
with wxPython shell extension library


## Getting Started

### Prerequisites

- Python 3.8 or later
    - mwxlib

### How to use

```python
from wxpyGL import glstream as gls
from wxpyGL import globject as glo

io = gls.basic_stream('teapot')
io.open()
io.objects += [
    glo.Teapot(shade=glo.silver),
    glo.Sphere(shade=glo.water, pos=(0,1,0), size=0.5),
]
io.run()
```


## Authors

* Kazuya O'moto - *Initial work* -

See also the list of who participated in this project.


## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details
