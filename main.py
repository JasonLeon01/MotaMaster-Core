from PySFBoost import *
from scripts.core import *
from scripts.scene import *

def setup():
    system.Config.init(['data/config/system.json', 'data/config/audio.json'])
    system.System.init('mota.ini')
    Time.TimeMgr.init()

    system.System.current_scene = title.Scene()

def clear():
    ResourceMgr.TextureMgr.clear()
    ResourceMgr.FontMgr.clear()
    ResourceMgr.AudioMgr.clear()
    Particle.ParticleMgr.clear()
    Animation.AnimationMgr.clear()

def main():
    setup()

    if system.System.current_scene is not None:
        system.System.current_scene.main()

    clear()

if __name__ == '__main__':
    main()
