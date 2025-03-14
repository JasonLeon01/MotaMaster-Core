# MotaMaster-Core

[中文](README-CN.md) | [English](README.md)

## Requirements & Installation
- Python Version: 3.9.0
- If you need to use Debug mode, install psutil.

## Installing PysfBoost
```
git clone https://github.com/JasonLeon01/PySFML.git
```

## Notes
For debugging, run `launcher-debug.py`:

```
python launcher.py
```

This script contains the same code as the executable launcher, allowing you to set breakpoints and debug efficiently.

- The project includes a built-in Python 3.9 interpreter, enabling the executable to run without requiring a separate Python installation. However, for debugging (e.g., setting breakpoints), installing Python and running launcher-debug.py is recommended.
- You can package the project using tools like nuitka or pyinstaller.
- When launching via mota.exe or launcher.py, all relative paths are resolved with respect to the project root directory.
