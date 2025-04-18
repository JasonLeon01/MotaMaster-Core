from PySFBoost.ResourceMgr import TextureMgr
from PySFBoost.sfSystem import Vector2f, Vector2u, Angle
from PySFBoost.sfGraphics import Sprite
from scripts.core.scene import SceneBase
from scripts.core.system import System
from scripts.core.window import WindowCommand
from scripts.core.graphics import Graphics

class Scene(SceneBase):
    def __init__(self):
        self.sprite = Sprite(TextureMgr.system("GrassBackground.png"))
        self.window = WindowCommand(320, [
            (WindowCommand.from_str("新游戏", Vector2u(288, 32)), self.new_game),
            (WindowCommand.from_str("加载游戏", Vector2u(288, 32)), self.load_game),
            (WindowCommand.from_str("退出", Vector2u(288, 32)), self.exit_game),
        ])
        self.window.set_origin(Vector2f(160, 64))
        self.window.set_position(Vector2f(320, 240))
        super().__init__()

    def on_start(self):
        Graphics.graphics_mgr.add(self.sprite, 0)
        Graphics.graphics_mgr.add(self.window, 0)

    def on_stop(self):
        Graphics.graphics_mgr.remove(self.sprite)
        Graphics.graphics_mgr.remove(self.window)

    def render_handle(self, delta_time):
        self.window.update(delta_time)
        self.window.rotate(Angle.degrees(1))
        super().render_handle(delta_time)

    def new_game(self):
        print("new game")

    def load_game(self):
        print("load game")

    def exit_game(self):
        print("exit game")
        System.current_scene = None
