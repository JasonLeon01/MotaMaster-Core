import bisect
import os
from typing import Dict, List
from PySFBoost import Animation, sfGraphics, Particle, Time, sfSystem
from . import system

class GraphicsMgr:
    def __init__(self):
        self._drawables: Dict[int, List[sfGraphics.Drawable]] = {}
        self._z_list = []
        self._drawable_to_z: Dict[sfGraphics.Drawable, int] = {}

    def add(self, drawable: sfGraphics.Drawable, z: int = 0):
        if drawable in self._drawable_to_z:
            raise ValueError('Drawable already exists.')
        if z not in self._drawables:
            self._drawables[z] = []
            bisect.insort(self._z_list, z)
        self._drawables[z].append(drawable)
        self._drawable_to_z[drawable] = z

    def remove(self, drawable: sfGraphics.Drawable):
        if drawable not in self._drawable_to_z:
            raise ValueError('Drawable not found.')
        z = self._drawable_to_z[drawable]
        self._drawables[z].remove(drawable)
        self._drawable_to_z.pop(drawable)
        if len(self._drawables[z]) == 0:
            self._drawables.pop(z)

    def clear(self):
        self._drawables.clear()
        self._z_list.clear()
        self._drawable_to_z.clear()

    def get_z_list(self):
        return self._z_list.copy()

    def display(self, target: sfGraphics.RenderTarget, z: int = None):
        if z is None:
            z_list = self.get_z_list()
        else:
            z_list = [z]
        for z in z_list:
            if z in self._drawables:
                for drawable in self._drawables[z]:
                    if isinstance(drawable, sfGraphics.Sprite):
                        drawable.get_texture().set_smooth(system.System.get_smooth())
                    target.draw(drawable)

class Graphics:
    graphics_mgr = GraphicsMgr()
    animation_mgr = Animation.AnimationMgr()
    particle_mgr = Particle.ParticleMgr()

    _frame_count = 0
    _debug_text: sfGraphics.Text = None
    _freeze_image: sfGraphics.Texture = None
    _freeze_sprite: sfGraphics.Sprite = None

    _canvas = None
    _canvas_sprite = None
    _transition: float = 0.0

    @classmethod
    def init(cls):
        cls._canvas = sfGraphics.RenderTexture(system.System.get_size().to_uint())
        cls._canvas_sprite = sfGraphics.Sprite(cls._canvas.get_texture())
        cls._canvas.clear(sfGraphics.Color.black())
        cls._canvas.display()
        cls._freeze_image: sfGraphics.Texture = sfGraphics.Texture(system.System.get_size().to_uint())
        cls._freeze_sprite: sfGraphics.Sprite = sfGraphics.Sprite(cls._freeze_image)

    @classmethod
    def update(cls, delta_time: float):
        if cls._canvas_sprite.get_scale().x != system.System.get_scale():
            scale = system.System.get_scale()
            cls._canvas_sprite.set_scale(sfSystem.Vector2f(scale, scale))

        cls._frame_count += 1
        cls._canvas.clear(sfGraphics.Color.transparent())
        graphics_z_list = cls.graphics_mgr.get_z_list()
        animation_z_list = cls.animation_mgr.get_z_list()
        particle_z_list = cls.particle_mgr.get_z_list()
        z_list = sorted(set(graphics_z_list + animation_z_list + particle_z_list))
        for z in z_list:
            if z in graphics_z_list:
                cls.graphics_mgr.display(cls._canvas, z)
            if z in animation_z_list:
                cls.animation_mgr.display(cls._canvas, z)
            if z in particle_z_list:
                cls.particle_mgr.display(cls._canvas, z)

        if cls._freeze_sprite is not None and cls._freeze_sprite.get_color().a > 0:
            speed = 255 * cls._transition * delta_time
            if cls._freeze_sprite.get_color().a - speed > 0:
                cls._freeze_sprite.set_color(sfGraphics.Color(255, 255, 255, int(cls._freeze_sprite.get_color().a - speed)))
            else:
                cls._freeze_sprite.set_color(sfGraphics.Color(255, 255, 255, 0))
            cls._canvas.draw(cls._freeze_sprite)

        if os.environ.get('DEBUG') == 'True':
            cls.debug_info(cls._canvas, delta_time)

        cls._canvas.display()
        cls._canvas.get_texture().set_smooth(system.System.get_smooth())
        system.System.window.draw(cls._canvas_sprite)

    @classmethod
    def debug_info(cls, target: sfGraphics.RenderTarget, delta_time: float):
        import psutil
        if cls._debug_text is None:
            cls._debug_text = sfGraphics.Text('')
            cls._debug_text.set_font(system.System.get_font())
            cls._debug_text.set_character_size(12)

        fps = 1.0 / delta_time
        average_fps = cls._frame_count / Time.TimeMgr.get_current_time()

        text = f'FPS: {fps:.2f}\n\(Average FPS: {average_fps:.2f})\n Memory: {psutil.Process().memory_info().rss / 1024 / 1024:.2f} MB'
        cls._debug_text.set_string(text)
        target.draw(cls._debug_text)

    @classmethod
    def freeze(cls):
        cls._freeze_image.update(cls._canvas.get_texture())
        cls._freeze_sprite.set_color(sfGraphics.Color(255, 255, 255, 255))

    @classmethod
    def transition(cls, duration: float = 1.0):
        cls._transition = duration