from operator import index
from PySFBoost.ResourceMgr import AudioMgr
from PySFBoost.sfSystem import Vector2u, Vector2f
from PySFBoost.sfGraphics import IntRect
from scripts.core import window
from scripts.core.viewport import Viewport
from scripts.core.system import Config, System
from scripts.core.window import Keyboard
from scripts.core.inputs import GameInput

class WindowConfig(window.WindowChoice):
    def __init__(self, x: int = 0, y: int = 0):
        rect = IntRect((x, y, 288, 160))
        super().__init__(rect, 20)
        self.items = [
            (WindowConfig.from_str('窗口大小：', Vector2u(128, 20), font_size=18), None),
            (WindowConfig.from_str('帧率：', Vector2u(128, 20), font_size=18), None),
            (WindowConfig.from_str('音乐：', Vector2u(128, 20), font_size=18), None),
            (WindowConfig.from_str('音效：', Vector2u(128, 20), font_size=18), None),
            (WindowConfig.from_str('语音：', Vector2u(128, 20), font_size=18), None),
        ]
        self.values = [
            (WindowConfig.from_str('', Vector2u(128, 20), font_size=18, text_pos=1), None),
            (WindowConfig.from_str('', Vector2u(128, 20), font_size=18, text_pos=1), None),
            (WindowConfig.from_str('', Vector2u(128, 20), font_size=18, text_pos=1), None),
            (WindowConfig.from_str('', Vector2u(128, 20), font_size=18, text_pos=1), None),
            (WindowConfig.from_str('', Vector2u(128, 20), font_size=18, text_pos=1), None),
        ]
        size = self.size.to_int()
        self.content = Viewport(IntRect((0, 0, size.x - 32, size.y - 32)))
        self.window_scale = System.get_scale()
        self.refresh()

    def render_handle(self, delta_time):
        if self.window_scale != System.get_scale():
            System.set_scale(self.window_scale)
        super().render_handle(delta_time)

    def logic_handle(self, delta_time):
        delta_op = 0
        if GameInput.trigger(Keyboard.Key.Left):
            delta_op = -1
        elif GameInput.trigger(Keyboard.Key.Right):
            delta_op = 1
        if delta_op != 0 or self.confirm():
            if delta_op == 0:
                mouse_pos = self.mouse_in_local()
                if mouse_pos.x > 192:
                    delta_op = 1
                else:
                    delta_op = -1
            AudioMgr.play_sound(Config.cursor_se)

            if self.index == 0:
                self.window_scale = System.get_scale()
                scale_range = [1.0, 2.0]
                if (delta_op > 0 and self.window_scale < scale_range[1]) or (delta_op < 0 and self.window_scale > scale_range[0]):
                    self.window_scale += 0.25 * delta_op
            elif self.index == 1:
                frame_rate = System.get_frame_rate()
                frame_rate_range = [30, 120]
                if (delta_op > 0 and frame_rate < frame_rate_range[1]) or (delta_op < 0 and frame_rate > frame_rate_range[0]):
                    frame_rate += 30 * delta_op
                    System.set_frame_rate(frame_rate)
            elif self.index == 2:
                AudioMgr.music_on = bool(delta_op + 1)
            elif self.index == 3:
                AudioMgr.sound_on = bool(delta_op + 1)
            elif self.index == 4:
                AudioMgr.voice_on = bool(delta_op + 1)
            self.refresh()

        return super().logic_handle(delta_time)

    def refresh(self):
        self.content.graphics_mgr.clear()
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
            text.set_position(Vector2f(0, 20 * i))
            self.content.graphics_mgr.add(text)

            text, _ = self.values[i]
            now_text = text_list[i]
            if text.get_text() != now_text:
                text.set_text(now_text)
                text.render()
            text.set_position(Vector2f(128, 20 * i))
            self.content.graphics_mgr.add(text)
