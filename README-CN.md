# MotaMaster-Core

[中文](README-CN.md) | [English](README.md)

## 需求与安装
- Python 版本：3.9.0
- 若需要使用调试模式，请安装 `psutil`。

## 安装 PysfBoost
```
git clone https://github.com/JasonLeon01/PySFML.git
```

## 注意事项
若要进行调试，请运行 `launcher-debug.py`:

```
python launcher.py
```

此脚本包含与可执行启动器相同的代码，可让你高效地设置断点并进行调试。

- 该项目包含一个内置的 Python 3.9 解释器，因此可执行文件无需单独安装 Python 即可运行。不过，若要进行调试（如设置断点），建议安装 Python 并运行 launcher-debug.py。
- 你可以使用 nuitka 或 pyinstaller 等工具打包项目。
- 通过 mota.exe 或 launcher.py 启动时，所有相对路径都相对于项目根目录解析。
