import os, sys
sys.path.append('./lib')
from PySFBoost.Time import *
from PySFBoost.sfGraphics import *
from PySFBoost.sfWindow import *
from PySFBoost.sfSystem import *
from PySFBoost.Video import *
TimeMgr.init()
window: RenderWindow = RenderWindow(VideoMode(Vector2u(800, 600)), "pysf video Test")
window.set_framerate_limit(60)
video_player = Video("330929291_da2-1-192.mp4", window)
video_player.play()