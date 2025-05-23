import bisect
import os
from typing import Dict, List
from PySFBoost.sfSystem import *
from PySFBoost.sfGraphics import *
from PySFBoost.Animation import *
from PySFBoost.Particle import *
from PySFBoost.Time import *
from .system import *

class GraphicsMgr:
    def __init__(self):
        self._drawables: Dict[int, List[Drawable]] = {}
        self._z_list = []
        self._drawable_to_z: Dict[Drawable, int] = {}

    def has(self, drawable: Drawable):
        return drawable in self._drawable_to_z

    def add(self, drawable: Drawable, z: int = 0):
        if drawable in self._drawable_to_z:
            raise ValueError('Drawable already exists.')
        if z not in self._drawables:
            self._drawables[z] = []
            bisect.insort(self._z_list, z)
        self._drawables[z].append(drawable)
        self._drawable_to_z[drawable] = z

    def remove(self, drawable: Drawable):
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

    def update(self, delta_time: float):
        for drawables in self._drawables.copy().values():
            for drawable in drawables[:]:
                if hasattr(drawable, 'update'):
                    drawable.update(delta_time)

    def display(self, target: RenderTarget, z: int = None):
        if z is None:
            z_list = self.get_z_list()
        else:
            z_list = [z]
        for z in z_list:
            if z in self._drawables:
                for drawable in self._drawables[z]:
                    target.draw(drawable)

class Graphics:
    graphics_mgr = GraphicsMgr()
    animation_mgr = AnimationMgr()
    particle_mgr = ParticleMgr()

    _frame_count = 0
    _debug_text: Text = None
    _freeze_image: Texture = None
    _freeze_sprite: Sprite = None

    transition_duration: float = 0.0

    @classmethod
    def update(cls, delta_time: float):
        cls._frame_count += 1
        System.window.clear(Color.transparent())
        graphics_z_list = cls.graphics_mgr.get_z_list()
        animation_z_list = cls.animation_mgr.get_z_list()
        particle_z_list = cls.particle_mgr.get_z_list()
        z_list = sorted(set(graphics_z_list + animation_z_list + particle_z_list))
        for z in z_list:
            if z in graphics_z_list:
                cls.graphics_mgr.display(System.window, z)
            if z in animation_z_list:
                cls.animation_mgr.display(System.window, z)
            if z in particle_z_list:
                cls.particle_mgr.display(System.window, z)

        if cls._freeze_sprite is not None and cls._freeze_sprite.get_color().a > 0:
            speed = 255 * cls.transition_duration * delta_time
            if cls._freeze_sprite.get_color().a - speed > 0:
                cls._freeze_sprite.set_color(Color(255, 255, 255, int(cls._freeze_sprite.get_color().a - speed)))
            else:
                cls._freeze_sprite.set_color(Color(255, 255, 255, 0))
            System.window.draw(cls._freeze_sprite)

        if cls._freeze_sprite is not None and cls._freeze_sprite.get_color().a == 0:
            cls.transition_duration = 0.0

        if os.environ.get('DEBUG') == 'True':
            cls.debug_info(System.window, delta_time)

    @classmethod
    def debug_info(cls, target: RenderTarget, delta_time: float):
        if cls._debug_text is None:
            cls._debug_text = Text(System.get_font()[0], '', 12)

        fps = 1.0 / delta_time
        average_fps = cls._frame_count / TimeMgr.get_current_time().as_seconds()
        text = f'FPS: {fps:.2f}\nAverage FPS: {average_fps:.2f}\n'
        try:
            import psutil
            text += f'CPU Usage: {psutil.cpu_percent()}%\n'
            text += f'CPU Cores: {psutil.cpu_count()}\n'
            text += f'CPU Frequency: {psutil.cpu_freq().current / 1000:.2f} GHz\n'
            text += f'Memory Usage:  {psutil.Process().memory_info().rss / 1024 / 1024:.2f} MB\n'
        except:
            text += 'Install psutil to get CPU and memory usage.\n'
        cls._debug_text.set_string(text)
        cls._debug_text.set_position(Vector2f(10, 10))
        target.draw(cls._debug_text)

    @classmethod
    def freeze(cls):
        if cls._freeze_image is None or cls._freeze_image.get_size() != System.window.get_size():
            cls._freeze_image = Texture(System.window.get_size())
            cls._freeze_sprite = Sprite(cls._freeze_image)
            cls._freeze_sprite.set_scale(Vector2f(1.0 / System.get_scale(), 1.0 / System.get_scale()))
        cls._freeze_image.update(System.window)
        cls._freeze_sprite.set_color(Color(255, 255, 255, 255))

    @classmethod
    def transition(cls, duration: float = 2.0):
        cls.transition_duration = duration

    @classmethod
    def clear(cls):
        cls.graphics_mgr.clear()
        cls.animation_mgr.clear()
        cls.particle_mgr.clear()
