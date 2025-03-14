from typing import Dict, List
from PySFBoost import ResourceMgr, sfGraphics, sfSystem
from . import viewport, system

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

        self.content: sfGraphics.RenderTexture = None
        self._content_sprite: sfGraphics.Sprite = None

        self._content_view = sfGraphics.RenderTexture(sfSystem.Vector2u(rect.size.x - 32, rect.size.y - 32))
        self._content_view_sprite = sfGraphics.Sprite(self._content_view.get_texture())
        self._content_view_sprite.set_position(sfSystem.Vector2f(16, 16))

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
        self._window_back_sprite.set_color(sfGraphics.Color(255, 255, 255, self.back_opacity))
        self._canvas.draw(self._window_back_sprite)
        self._canvas.draw(self._window_edge_sprite)

        self._content_view.clear(sfGraphics.Color.transparent())

        if self.content is not None:
            self.content.display()
            if self._content_sprite is None:
                self._content_sprite = sfGraphics.Sprite(self.content.get_texture())
            self._content_view.draw(self._content_sprite)
            self._content_view.display()
            self._content_sprite.set_color(sfGraphics.Color(255, 255, 255, self.content_opacity))
            self._content_view.draw(self._content_view_sprite)

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
            self._content_view.draw(self._rect_sprite)

        self._content_view.display()
        self._canvas.draw(self._content_view_sprite)
        return super().render_handle(delta_time)

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
    pass

class WindowChoice(WindowBase):
    pass

class WindowCommand(WindowBase):
    pass
