import math
from typing import Any, Callable, Dict, List, Tuple
from PySFBoost import ResourceMgr, sfGraphics, sfSystem, sfWindow, TextEnhance
from . import viewport, system, inputs

class Window(viewport.Viewport):
    def __init__(self, rect: sfGraphics.IntRect, asset: sfGraphics.Image = None, repeat: bool = False):
        super().__init__(rect)
        self._asset = asset
        if asset is None:
            self._asset = ResourceMgr.TextureMgr.system(system.Config.windowskin_file).copy_to_image()
        self.back_opacity = system.Config.window_opacity
        self.opacity = 255
        self.content_opacity = 255
        self._repeat = repeat

        self._window_edge = sfGraphics.RenderTexture(rect.size.to_uint())
        self._window_edge_sprite = sfGraphics.Sprite(self._window_edge.get_texture())
        self._window_back = sfGraphics.Texture(self._asset, False, sfGraphics.IntRect((0, 0, 128, 128)))

        self._rect: sfGraphics.RenderTexture = None
        self._rect_back = sfGraphics.Texture(self._asset, False, sfGraphics.IntRect((132, 68, 24, 24)))
        self._rect_sprite: sfGraphics.Sprite = None
        self.rect_fade_speed = 160
        self.rect_opacity = (160, 255)
        self._fade_in = False

        self._window_back.set_repeated(self._repeat)
        self._window_back_sprite = sfGraphics.Sprite(self._window_back)
        if self._repeat:
            self._window_back_sprite.set_texture_rect(sfGraphics.IntRect(sfSystem.Vector2i(0, 0), self.get_local_bounds().size.to_int()))
        else:
            self._window_back_sprite.set_scale(sfSystem.Vector2f(rect.size.x / 128.0, rect.size.y / 128.0))

        self.content: viewport.Viewport = None

        self._cached_corner: Dict[str, List[sfGraphics.Texture]] = {}
        self._cached_edges: Dict[str, List[sfGraphics.Texture]] = {}
        self._presave(self._cached_corner, {
                'window': [
                    sfGraphics.IntRect((128, 0, 16, 16)),
                    sfGraphics.IntRect((176, 0, 16, 16)),
                    sfGraphics.IntRect((128, 48, 16, 16)),
                    sfGraphics.IntRect((176, 48, 16, 16))
                ],
                'rect': [
                    sfGraphics.IntRect((128, 64, 4, 4)),
                    sfGraphics.IntRect((156, 64, 4, 4)),
                    sfGraphics.IntRect((128, 92, 4, 4)),
                    sfGraphics.IntRect((156, 92, 4, 4))
                ]
            }
        )
        self._presave(self._cached_edges, {
                'window': [
                    sfGraphics.IntRect((144, 0, 32, 16)),
                    sfGraphics.IntRect((144, 48, 32, 16)),
                    sfGraphics.IntRect((128, 16, 16, 32)),
                    sfGraphics.IntRect((176, 16, 16, 32))
                ],
                'rect': [
                    sfGraphics.IntRect((132, 64, 24, 4)),
                    sfGraphics.IntRect((132, 92, 24, 4)),
                    sfGraphics.IntRect((128, 68, 4, 24)),
                    sfGraphics.IntRect((156, 68, 4, 24))
                ]
            }
        )
        self._render_sides()
        self.render_count = 0

    def render_handle(self, delta_time: float):
        if self.content is not None:
            self.content.render_handle(delta_time)
            self.content.display()
        self._window_back_sprite.set_color(sfGraphics.Color(255, 255, 255, self.back_opacity))
        self._canvas.draw(self._window_back_sprite)
        self._canvas.draw(self._window_edge_sprite)

        if self.content is not None:
            self.content.set_color(sfGraphics.Color(255, 255, 255, self.content_opacity))
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
            self._rect_sprite.set_color(sfGraphics.Color(255, 255, 255, int(opacity)))
            self._canvas.draw(self._rect_sprite)

        super().render_handle(delta_time)

    def set_rect(self, rect: sfGraphics.IntRect):
        if (self._rect is None):
            self._rect = sfGraphics.RenderTexture(rect.size.to_uint())
            self._rect_sprite = sfGraphics.Sprite(self._rect.get_texture())
            self._render_rect(rect.size.to_uint())
            return
        if (self._rect.get_size() != rect.size.to_uint()):
            self._render_rect(rect.size.to_uint())
        self._rect_sprite.set_position(rect.position.to_float())

    def _presave(self, target: Dict[str, List[sfGraphics.Texture]], area_rects: Dict[str, List[sfGraphics.IntRect]]):
        for type_, area in area_rects.items():
            target[type_] = []
            for i in range(4):
                sub_texture = sfGraphics.Texture(self._asset, False, area[i])
                target[type_].append(sub_texture)

    def _render_corner(self, dst: sfGraphics.RenderTarget, area_caches: List[sfGraphics.Texture], positions: List[sfSystem.Vector2f]):
        for i in range(4):
            corner_sprite = sfGraphics.Sprite(area_caches[i])
            corner_sprite.set_position(positions[i])
            dst.draw(corner_sprite)

    def _render_edge(self, dst: sfGraphics.RenderTarget, area_caches: List[sfGraphics.Texture], target_scales: List[sfSystem.Vector2u], positions: List[sfSystem.Vector2f]):
        for i in range(4):
            texture = area_caches[i]
            texture.set_repeated(True)
            sprite = sfGraphics.Sprite(texture, sfGraphics.IntRect(sfSystem.Vector2i(0, 0), target_scales[i].to_int()))
            sprite.set_position(positions[i])
            dst.draw(sprite)

    def _render_sides(self):
        self._window_edge.clear(sfGraphics.Color.transparent())
        size = self.get_local_bounds().size
        corner_positions = [
            sfSystem.Vector2f(0, 0),
            sfSystem.Vector2f(size.x - 16, 0),
            sfSystem.Vector2f(0, size.y - 16),
            sfSystem.Vector2f(size.x - 16, size.y - 16)
        ]
        target_scales = [
            sfSystem.Vector2u(size.x - 32, 16),
            sfSystem.Vector2u(size.x - 32, 16),
            sfSystem.Vector2u(16, size.y - 32),
            sfSystem.Vector2u(16, size.y - 32)
        ]
        edge_positions = [
            sfSystem.Vector2f(16, 0),
            sfSystem.Vector2f(16, size.y - 16),
            sfSystem.Vector2f(0, 16),
            sfSystem.Vector2f(size.x - 16, 16)
        ]
        self._render_corner(self._window_edge, self._cached_corner['window'], corner_positions)
        self._render_edge(self._window_edge, self._cached_edges['window'], target_scales, edge_positions)

    def _render_rect(self, size: sfSystem.Vector2u):
        self._rect.clear(sfGraphics.Color.transparent())
        self._rect.resize(size)
        corner_positions = [
            sfSystem.Vector2f(0, 0),
            sfSystem.Vector2f(size.x - 4, 0),
            sfSystem.Vector2f(0, size.y - 4),
            sfSystem.Vector2f(size.x - 4, size.y - 4)
        ]
        target_scales = [
            sfSystem.Vector2u(size.x - 8, 4),
            sfSystem.Vector2u(size.x - 8, 4),
            sfSystem.Vector2u(4, size.y - 8),
            sfSystem.Vector2u(4, size.y - 8)
        ]
        edge_positions = [
            sfSystem.Vector2f(4, 0),
            sfSystem.Vector2f(4, size.y - 4),
            sfSystem.Vector2f(0, 4),
            sfSystem.Vector2f(size.x - 4, 4)
        ]
        self._render_corner(self._rect, self._cached_corner['rect'], corner_positions)
        self._render_edge(self._rect, self._cached_edges['rect'], target_scales, edge_positions)
        center_sprite = sfGraphics.Sprite(self._rect_back)
        center_sprite.set_scale(sfSystem.Vector2f((size.x - 8) / 24.0, (size.y - 8) / 24.0))
        center_sprite.set_position(sfSystem.Vector2f(4, 4))
        self._rect.draw(center_sprite)
        self._rect.display()

class WindowBase(Window):
    def mouse_in_rect(self) -> bool:
        mouse_pos = self.mouse_in_local()
        texture_size = self.get_texture().get_size()
        tex_x, tex_y = mouse_pos.x, mouse_pos.y
        return (tex_x >= 0 and tex_x < texture_size.x and tex_y >= 0 and tex_y < texture_size.y)

    def mouse_in_local(self) -> sfSystem.Vector2i:
        mouse_x, mouse_y = sfWindow.Mouse.get_position(system.System.window)
        mouse_pos = sfSystem.Vector2i(mouse_x, mouse_y)
        mouse_pos = (mouse_pos.to_float() / system.System.get_scale()).to_int()
        world_pos = system.System.window.map_pixel_to_coords(mouse_pos)
        local_pos = self.get_inverse_transform().transform_point(world_pos)
        texture_rect = self.get_texture_rect()
        texture_size = self.get_texture().get_size()
        tex_x = (local_pos.x - texture_rect.left()) / texture_rect.width() * texture_size.x
        tex_y = (local_pos.y - texture_rect.top()) / texture_rect.height() * texture_size.y
        return sfSystem.Vector2i(tex_x, tex_y)

    @staticmethod
    def from_str(text: str, size: sfSystem.Vector2u, font_index: int = 0):
        return TextEnhance.EText.from_str(text, system.System.get_font()[font_index], size, system.System.get_font_style_config())

class WindowChoice(WindowBase):
    def __init__(self, rect: sfGraphics.IntRect, cursor_height: int, cursor_width = None, column: int = 1, asset: sfGraphics.Image = None, repeat: bool = False):
        super().__init__(rect, asset, repeat)
        self.column = column
        self.cursor_width = cursor_width
        self.cursor_height = cursor_height
        self.index = 0
        self.items: List[Tuple[TextEnhance.EText, Callable[..., Any]]] = []
        self.active = True

    def rows(self) -> int:
        return int(math.ceil(1.0 * len(self.items) / self.column))

    def get_cursor_width(self):
        if self.cursor_width is not None:
            return self.cursor_width
        return self.get_local_bounds().size.x // self.column - 32

    def update_cursor_rect(self):
        if len(self.items) == 0 or self.index < 0:
            return

        row = self.index // self.column
        x = self.index % self.column * (self.get_cursor_width() + 32) + 16
        y = row * self.cursor_height + 16
        if self.content is not None:
            y -= self.content.get_origin().y
        self.set_rect(sfGraphics.IntRect(sfSystem.Vector2i(x, y), sfSystem.Vector2i(self.get_cursor_width(), self.cursor_height)))

    def confirm(self):
        if inputs.GameInput.trigger(sfWindow.Keyboard.Key.Enter) or inputs.GameInput.trigger(sfWindow.Keyboard.Key.Space):
            return True
        if self.mouse_in_rect():
            mouse_pos = self.mouse_in_local()
            if (mouse_pos.x >= 16 and mouse_pos.x <= self.get_local_bounds().size.x - 16 and mouse_pos.y >= 0 and mouse_pos.y <= self.cursor_height):
                if inputs.GameInput.left_click():
                    return True
        return False

    def cancel(self):
        if inputs.GameInput.trigger(sfWindow.Keyboard.Key.Escape):
            return True
        if inputs.GameInput.right_click():
            return True
        return False

    def _key_response(self, delta_time: float):
        if inputs.GameInput.repeat(sfWindow.Keyboard.Key.Up, 0.1, delta_time):
            if (self.column == 1 and inputs.GameInput.trigger(sfWindow.Keyboard.Key.Up)) or self.index >= self.column:
                self.index = (self.index - self.column + len(self.items)) % len(self.items)
                # ResourceMgr.AudioMgr.play_sound(system.Config.cursor_se)
                return
        if inputs.GameInput.repeat(sfWindow.Keyboard.Key.Down, 0.1, delta_time):
            if (self.column == 1 and inputs.GameInput.trigger(sfWindow.Keyboard.Key.Down)) or self.index < len(self.items) - self.column:
                self.index = (self.index + self.column) % len(self.items)
                ResourceMgr.AudioMgr.play_sound(system.Config.cursor_se)
                return
        if inputs.GameInput.repeat(sfWindow.Keyboard.Key.Left, 0.1, delta_time):
            if inputs.GameInput.trigger(sfWindow.Keyboard.Key.Left) or self.index > 0:
                self.index = (self.index - 1 + len(self.items)) % len(self.items)
                # ResourceMgr.AudioMgr.play_sound(system.Config.cursor_se)
                return
        if inputs.GameInput.repeat(sfWindow.Keyboard.Key.Right, 0.1, delta_time):
            if inputs.GameInput.trigger(sfWindow.Keyboard.Key.Right) or self.index < len(self.items) - 1:
                self.index = (self.index + 1) % len(self.items)
                # ResourceMgr.AudioMgr.play_sound(system.Config.cursor_se)
                return

    def _mouse_response(self, delta_time: float):
        if inputs.GameInput.wheel_up():
            self.index = (self.index - 1 + len(self.items)) % len(self.items)
            # ResourceMgr.AudioMgr.play_sound(system.Config.cursor_se)
            return
        if inputs.GameInput.wheel_down():
            self.index = (self.index + 1) % len(self.items)
            # ResourceMgr.AudioMgr.play_sound(system.Config.cursor_se)
            return

    def render(self, delta_time):
        super().render(delta_time)
        if self.content is not None:
            origin = self.content.get_origin()
            size = self.get_local_bounds().size
            if (self.index // self.column + 1) * self.cursor_height - origin.y > size.y - 32:
                origin.y = (self.index // self.column + 1) * self.cursor_height - size.y + 32
            if (self.index // self.column) * self.cursor_height - origin.y < 0:
                origin.y = (self.index // self.column) * self.cursor_height
            if (self.index % self.column + 1) * (self.get_cursor_width() + 32) - origin.x > size.x - 32:
                origin.x = (self.index % self.column + 1) * (self.get_cursor_width() + 32) - size.x + 32
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
        self._mouse_response(delta_time)
        if self.confirm():
            _, callback = self.items[self.index]
            callback()

class WindowCommand(WindowChoice):
    def __init__(self, width: int, commands: List[Tuple[TextEnhance.EText, Callable[..., Any]]], asset: sfGraphics.Image = None, repeat: bool = False):
        height = 32 * (len(commands) + 1)
        super().__init__(sfGraphics.IntRect((0, 0, width, height)), 32, None, 1, asset, repeat)
        self.items = commands
        self.content = viewport.Viewport(sfGraphics.IntRect((0, 0, width, height)))
        self.refresh()

    def refresh(self):
        self.content.graphics_mgr.clear()
        for i, (text, _) in enumerate(self.items):
            text.set_position(sfSystem.Vector2f(16, i * 32 + 16))
            self.content.graphics_mgr.add(text)
