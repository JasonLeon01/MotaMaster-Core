from PySFBoost.Time import TimeMgr
from PySFBoost.ResourceMgr import TextureMgr, FontMgr, AudioMgr
from scripts.core.system import System, Config
from scripts.core.graphics import Graphics
from scripts.scene import *

def setup():
    Config.init(['data/configs/system.json', 'data/configs/audio.json'])
    System.init('mota.ini')
    TimeMgr.init()
    Graphics.init()
    Graphics.freeze()
    System.current_scene = title.Scene()

def clear():
    System.window.clear()
    System.window.display()

    Graphics.clear()
    TextureMgr.clear()
    FontMgr.clear()
    AudioMgr.clear()

def main():
    setup()
    if System.current_scene is not None:
        System.current_scene.main()

    Graphics.transition(1)
    while Graphics.transition_duration > 0:
        delta_time = TimeMgr.get_delta_time().as_seconds()
        Graphics.update(delta_time)
        AudioMgr.update()
        System.window.display()

    clear()

if __name__ == '__main__':
    main()
