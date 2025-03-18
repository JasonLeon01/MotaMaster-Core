from scripts.core.scene import SceneBase
from scripts.core.window import WindowCommand
from scripts.core.graphics import Graphics
from scripts.core.system import System
from scripts.core.input import GameInput
from PySFBoost import sfSystem, sfGraphics, ResourceMgr, TextEnhance

class Scene(SceneBase):
    def __init__(self):
        self.sprite = sfGraphics.Sprite(ResourceMgr.TextureMgr.system("GrassBackground.png"))
        self.window = WindowCommand(320, [
            (WindowCommand.from_str("新游戏", sfSystem.Vector2u(288, 32)), self.new_game),
            (WindowCommand.from_str("加载游戏", sfSystem.Vector2u(288, 32)), self.load_game),
            (WindowCommand.from_str("退出", sfSystem.Vector2u(288, 32)), self.exit_game),
        ])
        super().__init__()

    def on_start(self):
        Graphics.graphics_mgr.add(self.sprite, 0)
        Graphics.graphics_mgr.add(self.window, 0)

    def render_handle(self, delta_time):
        self.window.update(delta_time)
        #self.window.rotate(sfSystem.Angle.degrees(1))
        super().render_handle(delta_time)

    def logic_handle(self, delta_time):
        if GameInput.left_click():
            print("left click")
        if GameInput.right_click():
            print("right click")
        if GameInput.middle_click():
            print("middle click")
        if self.window.cancel():
            print("cancel")
        super().logic_handle(delta_time)

    def new_game(self):
        print("new game")

    def load_game(self):
        print("load game")

    def exit_game(self):
        print("exit game")