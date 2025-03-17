from PySFBoost import *
from scripts.core import *
from scripts.scene import *

def setup():
    system.Config.init(['data/configs/system.json', 'data/configs/audio.json'])
    system.System.init('mota.ini')
    Time.TimeMgr.init()
    graphics.Graphics.init()
    graphics.Graphics.freeze()
    system.System.current_scene = title.Scene()

def clear():
    ResourceMgr.TextureMgr.clear()
    ResourceMgr.FontMgr.clear()
    ResourceMgr.AudioMgr.clear()

def main():
    setup()

    if system.System.current_scene is not None:
        system.System.current_scene.main()

    clear()

if __name__ == '__main__':
    main()
