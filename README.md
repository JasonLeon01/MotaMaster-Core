# MotaMaster-Core

English | [中文](README-CN.md)

## Requirements & Installation
- Python Version: 3.10.0
- If you need to use Debug mode, install psutil.
- This project uses [PySFBoost](https://github.com/JasonLeon01/PySFBoost), the Python bindings for SFML and some enhancing functions, for graphics and multimedia features.

## Installing PySFBoost
```
git clone https://github.com/JasonLeon01/PySFBoost.git
```

## Running
To run the project, you can use the following files:

### If you are using Windows:
- mota.exe: This is the main executable file for Windows, including python runtime. You don't have to install Python to run it.
- mota.bat: This is a bat file for Windows. It's lighter but doesn't include Python runtime.

### If you are using macOS:
- mota.command: This is a command file for macOS. It doesn't include Python runtime.

Before running it, you have to run the following command in your terminal to ensure the file is executable:

```shell
chmod +x mota.command
```

## Notes
For debugging, run `launcher-debug.py`:

```
python launcher-debug.py
```

This script contains the same code as the executable launcher, allowing you to set breakpoints and debug efficiently.

- The project includes a built-in Python 3.10 interpreter, enabling the executable to run without requiring a separate Python installation. However, for debugging (e.g., setting breakpoints), installing Python and running launcher-debug.py is recommended.
- You can package the project using tools like nuitka or pyinstaller.
- When launching via mota.exe, mota.command or launcher.py, all relative paths are resolved with respect to the project root directory.

## Licenses
- This project uses the [HarmonyOS Sans](https://developer.huawei.com/images/download/general/HarmonyOS-Sans.zip) font. For license details, please refer to `assets/fonts/LICENSE.txt`.

## External libraries
- [PySFBoost](https://github.com/JasonLeon01/PySFBoost) is under the [zlib/libpng license](https://opensource.org/licenses/Zlib).
- [HarmonyOS Sans](https://developer.huawei.com/images/download/general/HarmonyOS-Sans.zip) is under the [HarmonyOS Sans Fonts License Agreement](assets/fonts/LICENSE.txt).
