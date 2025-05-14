from PySFBoost.ResourceMgr import *
from PySFBoost.sfSystem import *
from PySFBoost.sfGraphics import *
from scripts.core.scene import *
from scripts.core.system import *
from scripts.core.window import *
from scripts.core.graphics import *

from scripts.components.config import WindowConfig

class Scene(SceneBase):
    def __init__(self):
        self.sprite = Sprite(TextureMgr.system('GrassBackground.png'))
        self.title = GameWindow.from_str('\s[48]**MOTAMASTER**\s[18]\nmota\_python\_framework', Vector2u(480, 96), text_pos=1)
        self.title.set_origin(Vector2f(240, 48))
        self.title.set_position(Vector2f(320, 96))

        texts = [
            ('新游戏', self.new_game),
            ('加载游戏', self.load_game),
            ('设置', self.setting),
            ('退出', self.exit_game)
        ]
        if (os.path.exists('./save/default.sav')):
            texts.insert(0, ('进入游戏', self.enter_game))
        self.command_window = WindowCommand(288, [
            (WindowCommand.from_str(text, Vector2u(256, 32), text_pos=1), callback)
            for text, callback in texts
        ])
        self.command_window.centre()
        self.command_window.set_position(Vector2f(320, 320))

        self.config_window = WindowConfig(320, 320, 192)
        self.config_window.centre()

        super().__init__()

    def on_start(self):
        Graphics.graphics_mgr.add(self.sprite, 0)
        Graphics.graphics_mgr.add(self.title, 0)
        Graphics.graphics_mgr.add(self.command_window, 0)

    def on_stop(self):
        Graphics.graphics_mgr.remove(self.sprite)
        if Graphics.graphics_mgr.has(self.command_window):
            Graphics.graphics_mgr.remove(self.command_window)
        if Graphics.graphics_mgr.has(self.config_window):
            Graphics.graphics_mgr.remove(self.config_window)

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

    def enter_game(self):
        print('enter game')
        AudioMgr.play_sound(Config.decision_se)

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
