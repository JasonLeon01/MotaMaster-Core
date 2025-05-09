from PySFBoost.ResourceMgr import AudioMgr, TextureMgr
from PySFBoost.sfSystem import Vector2f, Vector2u
from PySFBoost.sfGraphics import Sprite
from scripts.core.scene import SceneBase
from scripts.core.system import Config, System
from scripts.core.window import WindowCommand
from scripts.core.graphics import Graphics

from scripts.components.config import WindowConfig

class Scene(SceneBase):
    def __init__(self):
        self.sprite = Sprite(TextureMgr.system('GrassBackground.png'))
        self.command_window = WindowCommand(288, [
            (WindowCommand.from_str('新游戏', Vector2u(256, 32), text_pos=1), self.new_game),
            (WindowCommand.from_str('加载游戏', Vector2u(256, 32), text_pos=1), self.load_game),
            (WindowCommand.from_str('设置', Vector2u(256, 32), text_pos=1), self.setting),
            (WindowCommand.from_str('退出', Vector2u(256, 32), text_pos=1), self.exit_game),
        ])
        self.command_window.set_origin(Vector2f(144, 64))
        self.command_window.set_position(Vector2f(320, 320))

        self.config_window = WindowConfig(320, 320)
        self.config_window.set_origin(Vector2f(144, 64))

        super().__init__()

    def on_start(self):
        Graphics.graphics_mgr.add(self.sprite, 0)
        Graphics.graphics_mgr.add(self.command_window, 0)

    def on_stop(self):
        Graphics.graphics_mgr.remove(self.sprite)
        Graphics.graphics_mgr.remove(self.command_window)

    def render_handle(self, delta_time):
        if Graphics.graphics_mgr.has(self.command_window):
            self.command_window.update(delta_time)
        if Graphics.graphics_mgr.has(self.config_window):
            self.config_window.update(delta_time)
        super().render_handle(delta_time)

    def logic_handle(self, delta_time: float):
        if Graphics.graphics_mgr.has(self.config_window):
            if self.config_window.cancel():
                AudioMgr.play_sound(Config.cancel_se)
                Graphics.graphics_mgr.remove(self.config_window)
                Graphics.graphics_mgr.add(self.command_window, 0)
                System.save_ini()
        return super().logic_handle(delta_time)

    def new_game(self):
        print('new game')
        AudioMgr.play_sound(Config.decision_se)

    def load_game(self):
        print('load game')
        AudioMgr.play_sound(Config.decision_se)

    def setting(self):
        AudioMgr.play_sound(Config.decision_se)
        Graphics.graphics_mgr.remove(self.command_window)
        Graphics.graphics_mgr.add(self.config_window, 0)

    def exit_game(self):
        AudioMgr.play_sound(Config.decision_se)
        System.current_scene = None
