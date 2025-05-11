from operator import index
from PySFBoost.ResourceMgr import *
from PySFBoost.sfSystem import *
from PySFBoost.sfGraphics import *
from scripts.core import *
from scripts.core.system import *
from scripts.core.window import *
from scripts.core.inputs import *

class WindowConfig(window.WindowChoice):
    def __init__(self, x: int = 0, y: int = 0):
        rect = IntRect((x, y, 288, 160))
        super().__init__(rect, 28)
        self.items = [
            (WindowConfig.from_str('窗口大小：', Vector2u(128, 28), font_size=20), None),
            (WindowConfig.from_str('帧率：', Vector2u(128, 28), font_size=20), None),
            (WindowConfig.from_str('音乐：', Vector2u(128, 28), font_size=20), None),
            (WindowConfig.from_str('音效：', Vector2u(128, 28), font_size=20), None),
            (WindowConfig.from_str('语音：', Vector2u(128, 28), font_size=20), None),
        ]
        self.values = [
            (WindowConfig.from_str('', Vector2u(128, 28), font_size=20, text_pos=1), None),
            (WindowConfig.from_str('', Vector2u(128, 28), font_size=20, text_pos=1), None),
            (WindowConfig.from_str('', Vector2u(128, 28), font_size=20, text_pos=1), None),
            (WindowConfig.from_str('', Vector2u(128, 28), font_size=20, text_pos=1), None),
            (WindowConfig.from_str('', Vector2u(128, 28), font_size=20, text_pos=1), None),
        ]
        size = self.size.to_int()
        self.content = RenderTexture(Vector2u(size.x - 32, len(self.items) * 28))
        self.window_scale = System.get_scale()
        self.refresh()

        self.delta_op = 0

    def render_handle(self, delta_time):
        if self.window_scale != System.get_scale():
            System.set_scale(self.window_scale)
        super().render_handle(delta_time)

    def on_click(self, mouse_pos: Vector2i):
        index = self.index
        super().on_click(mouse_pos)
        if index == self.index:
            if mouse_pos.x > 192:
                self.delta_op = 1
            else:
                self.delta_op = -1

    def logic_handle(self, delta_time):
        if GameInput.trigger(Keyboard.Key.Left):
            self.delta_op = -1
        elif GameInput.trigger(Keyboard.Key.Right):
            self.delta_op = 1
        if self.delta_op != 0:
            AudioMgr.play_sound(Config.cursor_se)

            if self.index == 0:
                self.window_scale = System.get_scale()
                scale_range = [1.0, 2.0]
                if (self.delta_op > 0 and self.window_scale < scale_range[1]) or (self.delta_op < 0 and self.window_scale > scale_range[0]):
                    self.window_scale += 0.25 * self.delta_op
            elif self.index == 1:
                frame_rate = System.get_frame_rate()
                frame_rate_range = [30, 120]
                if (self.delta_op > 0 and frame_rate < frame_rate_range[1]) or (self.delta_op < 0 and frame_rate > frame_rate_range[0]):
                    frame_rate += 30 * self.delta_op
                    System.set_frame_rate(frame_rate)
            elif self.index == 2:
                AudioMgr.music_on = bool(self.delta_op + 1)
            elif self.index == 3:
                AudioMgr.sound_on = bool(self.delta_op + 1)
            elif self.index == 4:
                AudioMgr.voice_on = bool(self.delta_op + 1)
            self.refresh()
            self.delta_op = 0

        return super().logic_handle(delta_time)

    def refresh(self):
        self.content.clear(Color.transparent())
        window_size = {
            1.0: '640x480',
            1.25: '800x600',
            1.5: '960x720',
            1.75: '1120x840',
            2.0: '1280x960'
        }
        opened = {
            True: '开',
            False: '关'
        }

        text_list = [
            str(window_size[self.window_scale]),
            str(System.get_frame_rate()),
            opened[AudioMgr.music_on],
            opened[AudioMgr.sound_on],
            opened[AudioMgr.voice_on]
        ]

        for i in range(5):
            text, _ = self.items[i]
            text.set_position(Vector2f(0, 28 * i))
            self.content.draw(text)

            text, _ = self.values[i]
            now_text = text_list[i]
            if text.get_text() != now_text:
                text.set_text(now_text)
                text.render()
            text.set_position(Vector2f(128, 28 * i))
            self.content.draw(text)

        self.content.display()
