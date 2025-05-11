import math
from typing import Any, Callable, Dict, List, Optional, Tuple
from PySFBoost.ResourceMgr import *
from PySFBoost.sfSystem import *
from PySFBoost.sfGraphics import *
from PySFBoost.sfWindow import *
from PySFBoost.TextEnhance import *
from .viewport import *
from .system import *
from .inputs import *

class Window(Viewport):
    def __init__(self, rect: IntRect, asset: Image = None, repeat: bool = False):
        super().__init__(rect)
        self._asset = asset
        if asset is None:
            self._asset = TextureMgr.system(Config.windowskin_file).copy_to_image()
        self.back_opacity = Config.window_opacity
        self.opacity = 255
        self.content_opacity = 255
        self._repeat = repeat

        self._window_edge = RenderTexture(rect.size.to_uint())
        self._window_edge.set_smooth(True)
        self._window_edge_sprite = Sprite(self._window_edge.get_texture())
        self._window_back = Texture(self._asset, False, IntRect((0, 0, 128, 128)))
        self._window_back.set_repeated(self._repeat)
        self._window_back_sprite = Sprite(self._window_back)

        self._rect: RenderTexture = None
        self._rect_sprite: Sprite = None
        self._rect_back = Texture(self._asset, False, IntRect((132, 68, 24, 24)))
        self._rect_back_sprite = Sprite(self._rect_back)
        self.rect_fade_speed = 160
        self.rect_opacity = (128, 255)
        self._fade_in = False

        if self._repeat:
            self._window_back_sprite.set_texture_rect(IntRect(Vector2i(0, 0), self.get_local_bounds().size.to_int()))
        else:
            self._window_back_sprite.set_scale(Vector2f(rect.size.x / 128.0, rect.size.y / 128.0))

        self.content: Viewport = None

        self._cached_corner: Dict[str, List[Texture]] = {}
        self._cached_edges: Dict[str, List[Texture]] = {}
        self._presave(self._cached_corner, {
                'window': [
                    IntRect((128, 0, 16, 16)),
                    IntRect((176, 0, 16, 16)),
                    IntRect((128, 48, 16, 16)),
                    IntRect((176, 48, 16, 16))
                ],
                'rect': [
                    IntRect((128, 64, 4, 4)),
                    IntRect((156, 64, 4, 4)),
                    IntRect((128, 92, 4, 4)),
                    IntRect((156, 92, 4, 4))
                ]
            }
        )
        self._presave(self._cached_edges, {
                'window': [
                    IntRect((144, 0, 32, 16)),
                    IntRect((144, 48, 32, 16)),
                    IntRect((128, 16, 16, 32)),
                    IntRect((176, 16, 16, 32))
                ],
                'rect': [
                    IntRect((132, 64, 24, 4)),
                    IntRect((132, 92, 24, 4)),
                    IntRect((128, 68, 4, 24)),
                    IntRect((156, 68, 4, 24))
                ]
            }
        )
        self._render_sides()
        self.render_count = 0

    @property
    def size(self):
        return self.get_local_bounds().size

    def render_handle(self, delta_time: float):
        if self.content is not None:
            self.content.clear()
            self.content.render_handle(delta_time)
            self.content.display()
        self._window_back_sprite.set_color(Color(255, 255, 255, self.back_opacity))
        self._canvas.draw(self._window_back_sprite)
        self._canvas.draw(self._window_edge_sprite)

        if self.content is not None:
            self.content.set_color(Color(255, 255, 255, self.content_opacity))
            content_view_size = self._content_view_size()
            self.content.set_view(View(FloatRect(self.content.get_origin(), content_view_size)))
            self.content.set_position(Vector2f(16 + self.content.get_origin().x, 16 + self.content.get_origin().y))
            self._canvas.draw(self.content)

        if self._rect is not None:
            opacity = self._rect_sprite.get_color().a
            speed = self.rect_fade_speed * delta_time
            if self._fade_in:
                opacity += speed
            else:
                opacity -= speed
            min_opacity, max_opacity = self.rect_opacity
            if opacity >= max_opacity:
                opacity = max_opacity
                self._fade_in = False
            if opacity <= min_opacity:
                opacity = min_opacity
                self._fade_in = True
            self._rect_sprite.set_color(Color(255, 255, 255, int(opacity)))
            self._canvas.draw(self._rect_sprite)

        super().render_handle(delta_time)

    def set_window_rect(self, rect: IntRect):
        self._canvas = RenderTexture(rect.size.to_uint())
        self._canvas.set_smooth(True)
        self.set_texture(self._canvas.get_texture())
        self.set_texture_rect(IntRect(Vector2i(0, 0), rect.size.to_int()))
        self._window_edge = RenderTexture(rect.size.to_uint())
        self._window_edge.set_smooth(True)
        self._window_edge_sprite = Sprite(self._window_edge.get_texture())
        if not self._repeat:
            self._window_back_sprite.set_scale(Vector2f(rect.size.x / 128.0, rect.size.y / 128.0))
        self._render_sides()

    def set_rect(self, rect: IntRect):
        if self._rect is None or self._rect.get_size() != rect.size.to_uint():
            self._rect = RenderTexture(rect.size.to_uint())
            self._rect.set_smooth(True)
            self._rect_sprite = Sprite(self._rect.get_texture())
            self._render_rect(rect.size.to_uint())
        self._rect_sprite.set_position(rect.position.to_float())

    def _presave(self, target: Dict[str, List[Texture]], area_rects: Dict[str, List[IntRect]]):
        for type_, area in area_rects.items():
            target[type_] = []
            for i in range(4):
                sub_texture = Texture(self._asset, False, area[i])
                target[type_].append(sub_texture)

    def _render_corner(self, dst: RenderTarget, area_caches: List[Texture], positions: List[Vector2f]):
        for i in range(4):
            corner_sprite = Sprite(area_caches[i])
            corner_sprite.set_position(positions[i])
            dst.draw(corner_sprite)

    def _render_edge(self, dst: RenderTarget, area_caches: List[Texture], target_scales: List[Vector2u], positions: List[Vector2f]):
        for i in range(4):
            texture = area_caches[i]
            texture.set_repeated(True)
            sprite = Sprite(texture, IntRect(Vector2i(0, 0), target_scales[i].to_int()))
            sprite.set_position(positions[i])
            dst.draw(sprite)

    def _render_sides(self):
        self._window_edge.clear(Color.transparent())
        corner_positions = [
            Vector2f(0, 0),
            Vector2f(self.size.x - 16, 0),
            Vector2f(0, self.size.y - 16),
            Vector2f(self.size.x - 16, self.size.y - 16)
        ]
        target_scales = [
            Vector2u(self.size.x - 32, 16),
            Vector2u(self.size.x - 32, 16),
            Vector2u(16, self.size.y - 32),
            Vector2u(16, self.size.y - 32)
        ]
        edge_positions = [
            Vector2f(16, 0),
            Vector2f(16, self.size.y - 16),
            Vector2f(0, 16),
            Vector2f(self.size.x - 16, 16)
        ]
        self._render_corner(self._window_edge, self._cached_corner['window'], corner_positions)
        self._render_edge(self._window_edge, self._cached_edges['window'], target_scales, edge_positions)
        self._window_edge.display()

    def _render_rect(self, size: Vector2u):
        corner_positions = [
            Vector2f(0, 0),
            Vector2f(size.x - 4, 0),
            Vector2f(0, size.y - 4),
            Vector2f(size.x - 4, size.y - 4)
        ]
        target_scales = [
            Vector2u(size.x - 8, 4),
            Vector2u(size.x - 8, 4),
            Vector2u(4, size.y - 8),
            Vector2u(4, size.y - 8)
        ]
        edge_positions = [
            Vector2f(4, 0),
            Vector2f(4, size.y - 4),
            Vector2f(0, 4),
            Vector2f(size.x - 4, 4)
        ]
        self._render_corner(self._rect, self._cached_corner['rect'], corner_positions)
        self._render_edge(self._rect, self._cached_edges['rect'], target_scales, edge_positions)
        self._rect_back_sprite.set_scale(Vector2f((size.x - 8) / 24.0, (size.y - 8) / 24.0))
        self._rect_back_sprite.set_position(Vector2f(4, 4))
        self._rect.draw(self._rect_back_sprite)
        self._rect.display()

    def _content_view_size(self):
        return Vector2f(self.size.x - 32, self.size.y - 32)

class WindowBase(Window):
    def mouse_in_rect(self) -> bool:
        mouse_pos = self.mouse_in_local()
        texture_size = self.get_texture().get_size()
        tex_x, tex_y = mouse_pos.x, mouse_pos.y
        return (tex_x >= 0 and tex_x < texture_size.x and tex_y >= 0 and tex_y < texture_size.y)

    def mouse_in_local(self) -> Vector2i:
        mouse_x, mouse_y = Mouse.get_position(System.window)
        mouse_pos = Vector2i(mouse_x, mouse_y)
        mouse_pos = (mouse_pos.to_float()).to_int()
        world_pos = System.window.map_pixel_to_coords(mouse_pos)
        local_pos = self.get_inverse_transform().transform_point(world_pos)
        texture_rect = self.get_texture_rect()
        texture_size = self.get_texture().get_size()
        tex_x = (local_pos.x - texture_rect.left()) / texture_rect.width() * texture_size.x
        tex_y = (local_pos.y - texture_rect.top()) / texture_rect.height() * texture_size.y
        return Vector2i(tex_x, tex_y)

    @staticmethod
    def from_str(text: str, size: Vector2u, font: Font = None, font_size: Optional[int] = None, text_pos: int = 0):
        if font is None:
            font = System.get_font()[0]
        style_config = System.get_font_style_config().copy()
        if font_size is not None:
            style_config.base_size = font_size
        return EText.from_str(text, font, size, style_config, text_pos)

class WindowChoice(WindowBase):
    def __init__(self, rect: IntRect, cursor_height: int, cursor_width = None, column: int = 1, asset: Image = None, repeat: bool = False):
        super().__init__(rect, asset, repeat)
        self.column = column
        self.cursor_width = cursor_width
        self.cursor_height = cursor_height
        self.index = 0
        self.items: List[Tuple[EText, Optional[Callable[..., Any]]]] = []
        self.active = True

    def rows(self) -> int:
        return int(math.ceil(1.0 * len(self.items) / self.column))

    def get_cursor_width(self):
        if self.cursor_width is not None:
            return self.cursor_width
        return self.size.x // self.column - 32

    def update_cursor_rect(self):
        if len(self.items) == 0 or self.index < 0:
            return

        row = self.index // self.column
        x = (self.index % self.column) * (self.get_cursor_width() + 32) + 16
        y = row * self.cursor_height + 16
        if self.content is not None:
            y -= self.content.get_origin().y
        self.set_rect(IntRect(Vector2i(x, y), Vector2i(self.get_cursor_width(), self.cursor_height)))

    def confirm(self):
        if GameInput.trigger(Keyboard.Key.Enter) or GameInput.trigger(Keyboard.Key.Space):
            return True
        if GameInput.left_click():
            mouse_pos = self.mouse_in_local()
            texture_size = self.get_texture().get_size()
            if (mouse_pos.x >= 16 and mouse_pos.x <= texture_size.x - 16 and mouse_pos.y >= 16 and mouse_pos.y <= texture_size.y - 16):
                actual_y = mouse_pos.y - 16 - self.content.get_origin().y
                actual_x = mouse_pos.x - 16 - self.content.get_origin().x
                row = actual_y // self.cursor_height
                col = actual_x // (self.get_cursor_width() + 32)
                index = int(row * self.column + col)
                if index < len(self.items):
                    if index != self.index:
                        self.index = index
                        AudioMgr.play_sound(Config.cursor_se)
                    else:
                        return True
        return False

    def cancel(self):
        if GameInput.trigger(Keyboard.Key.Escape):
            return True
        if GameInput.right_click():
            return True
        return False

    def _key_response(self, delta_time: float):
        if GameInput.repeat(Keyboard.Key.Up, 0.1, delta_time):
            if (self.column == 1 and GameInput.trigger(Keyboard.Key.Up)) or self.index >= self.column:
                self.index = (self.index - self.column + len(self.items)) % len(self.items)
                AudioMgr.play_sound(Config.cursor_se)
                return
        if GameInput.repeat(Keyboard.Key.Down, 0.1, delta_time):
            if (self.column == 1 and GameInput.trigger(Keyboard.Key.Down)) or self.index < len(self.items) - self.column:
                self.index = (self.index + self.column) % len(self.items)
                AudioMgr.play_sound(Config.cursor_se)
                return
        if self.column > 1:
            if GameInput.repeat(Keyboard.Key.Left, 0.1, delta_time):
                if GameInput.trigger(Keyboard.Key.Left) or self.index > 0:
                    self.index = (self.index - 1 + len(self.items)) % len(self.items)
                    AudioMgr.play_sound(Config.cursor_se)
                    return
            if GameInput.repeat(Keyboard.Key.Right, 0.1, delta_time):
                if GameInput.trigger(Keyboard.Key.Right) or self.index < len(self.items) - 1:
                    self.index = (self.index + 1) % len(self.items)
                    AudioMgr.play_sound(Config.cursor_se)
                    return

    def _wheel_response(self, delta_time: float):
        if self.mouse_in_rect():
            if GameInput.wheel_up():
                self.index = (self.index - 1 + len(self.items)) % len(self.items)
                AudioMgr.play_sound(Config.cursor_se)
                return
            if GameInput.wheel_down():
                self.index = (self.index + 1) % len(self.items)
                AudioMgr.play_sound(Config.cursor_se)
                return

    def render_handle(self, delta_time):
        super().render_handle(delta_time)
        if self.content is not None:
            origin = self.content.get_origin()
            if (self.index // self.column + 1) * self.cursor_height - origin.y > self.size.y - 32:
                origin.y = (self.index // self.column + 1) * self.cursor_height - self.size.y + 32
            if (self.index // self.column) * self.cursor_height - origin.y < 0:
                origin.y = (self.index // self.column) * self.cursor_height
            if (self.index % self.column + 1) * (self.get_cursor_width() + 32) - origin.x > self.size.x - 32:
                origin.x = (self.index % self.column + 1) * (self.get_cursor_width() + 32) - self.size.x + 32
            if (self.index % self.column) * (self.get_cursor_width() + 32) - origin.x < 0:
                origin.x = (self.index % self.column) * (self.get_cursor_width() + 32)

            if origin.y != self.content.get_origin().y or origin.x!= self.content.get_origin().x:
                self.content.set_origin(origin)
        self.update_cursor_rect()

    def logic_handle(self, delta_time: float):
        super().logic_handle(delta_time)
        if not self.active:
            return

        self._key_response(delta_time)
        self._wheel_response(delta_time)
        if self.confirm():
            _, callback = self.items[self.index]
            if callable(callback):
                callback()

class WindowCommand(WindowChoice):
    def __init__(self, width: int, commands: List[Tuple[EText, Callable[..., Any]]], asset: Image = None, repeat: bool = False):
        height = 32 * (len(commands) + 1)
        super().__init__(IntRect((0, 0, width, height)), 32, None, 1, asset, repeat)
        self.items = commands
        self.content = Viewport(IntRect((0, 0, width - 32, height - 32)))
        self.refresh()

    def refresh(self):
        self.content.graphics_mgr.clear()
        for i, (text, _) in enumerate(self.items):
            text.set_position(Vector2f(0, i * 32))
            self.content.graphics_mgr.add(text)
