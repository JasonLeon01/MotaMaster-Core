import bisect
import os
from typing import Dict, List, Tuple
from PySFBoost import Animation, sfGraphics, Particle, Time
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
                    target.draw(drawable)

class Graphics:
    graphics_mgr = GraphicsMgr()
    animation_mgr = Animation.AnimationMgr()
    particle_mgr = Particle.ParticleMgr()

    _frame_count = 0
    _debug_text: sfGraphics.Text = None
    _freeze_image: Tuple[sfGraphics.Texture, sfGraphics.Image] = None

    @classmethod
    def update(cls, delta_time: float):
        cls._frame_count += 1
        system.System.window.clear(sfGraphics.Color.transparent())
        if cls._freeze_image is not None:
            _, sprite = cls._freeze_image
            system.System.window.draw(sprite)
        else:
            graphics_z_list = cls.graphics_mgr.get_z_list()
            animation_z_list = cls.animation_mgr.get_z_list()
            particle_z_list = Particle.ParticleMgr.get_z_list()
            z_list = sorted(set(graphics_z_list + animation_z_list + particle_z_list))
            for z in z_list:
                if z in graphics_z_list:
                    cls.graphics_mgr.display(system.System.window, z)
                if z in animation_z_list:
                    cls.animation_mgr.display(system.System.window, z)
                if z in particle_z_list:
                    cls.particle_mgr.display(system.System.window, z)
        if os.environ.get('DEBUG') == 'True':
            cls.debug_info(system.System.window, delta_time)

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
        texture = sfGraphics.Texture()
        texture.update(system.System.window)
        cls._freeze_image = (texture, sfGraphics.Sprite(texture))

