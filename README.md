# MotaMaster-Core

[中文](README-CN.md) | [English](README.md)

## Requirements & Installation
- Python Version: 3.10.0
- If you need to use Debug mode, install psutil.
- This project uses [PySFML](https://github.com/JasonLeon01/PySFML), the Python bindings for SFML, for graphics and multimedia features.

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

- The project includes a built-in Python 3.10 interpreter, enabling the executable to run without requiring a separate Python installation. However, for debugging (e.g., setting breakpoints), installing Python and running launcher-debug.py is recommended.
- You can package the project using tools like nuitka or pyinstaller.
- When launching via mota.exe, mota.command or launcher.py, all relative paths are resolved with respect to the project root directory.

## Licenses
- This project uses the [HarmonyOS Sans](https://developer.huawei.com/images/download/general/HarmonyOS-Sans.zip) font. For license details, please refer to `assets/fonts/LICENSE.txt`.

## External libraries
- [PySFML](https://github.com/JasonLeon01/PySFML) is under the [zlib/libpng license](https://opensource.org/licenses/Zlib).
- [HarmonyOS Sans](https://developer.huawei.com/images/download/general/HarmonyOS-Sans.zip) is under the [HarmonyOS Sans Fonts License Agreement](assets/fonts/LICENSE.txt).
