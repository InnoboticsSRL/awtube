## Python API to interact with the AWTube robot using GBC

The code included in this repo is a library used to interact with the AWTube robot. It represents the functionality of the robot.

### Create virtual environment
``` python -m pip install virtualenv ```

```  python<version> -m venv <virtual-environment-name> ```
### To activate
``` source <virtual-environment-name>/bin/activate ```

### To build
``` python3 -m build``` build a .tar.gz and a .whl in `dist/` as explained [here](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#packaging-your-project)

### To build docs
``` cd docs ```
``` make clean ```
``` make html ```
