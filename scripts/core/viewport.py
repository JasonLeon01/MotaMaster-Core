from functools import partial
import traceback
from concurrent.futures import ThreadPoolExecutor
from PySFBoost.Animation import AnimationMgr
from PySFBoost.Particle import ParticleMgr
from PySFBoost.sfGraphics import RenderTexture, Sprite, Color, IntRect
from .graphics import GraphicsMgr

class Viewport(Sprite):
    def __init__(self, rect: IntRect):
        self.graphics_mgr = GraphicsMgr()
        self.animation_mgr = AnimationMgr()
        self.particle_mgr = ParticleMgr()
        self._canvas = RenderTexture(rect.size.to_uint())
        self._executor = ThreadPoolExecutor(max_workers = 1)

        super().__init__(self._canvas.get_texture())
        self.set_position(rect.position.to_float())

    def update(self, delta_time: float):
        self._canvas.clear(Color.transparent())
        logical_future = self._executor.submit(partial(self.logic_handle, delta_time))

        self.render_handle(delta_time)

        try:
            logical_future.result()
        except Exception as e:
            print(f"Thread execution failed: {e}\n{traceback.format_exc()}")

        self._canvas.display()

    def logic_handle(self, delta_time: float):
        pass

    def render_handle(self, delta_time: float):
        self.animation_mgr.update(delta_time)
        self.particle_mgr.update(delta_time)
        graphics_z_list = self.graphics_mgr.get_z_list()
        animation_z_list = self.animation_mgr.get_z_list()
        particle_z_list = self.particle_mgr.get_z_list()
        z_list = sorted(set(graphics_z_list + animation_z_list + particle_z_list))
        for z in z_list:
            if z in graphics_z_list:
                self.graphics_mgr.display(self._canvas, z)
            if z in animation_z_list:
                self.animation_mgr.display(self._canvas, z)
            if z in particle_z_list:
                self.particle_mgr.display(self._canvas, z)

    def clear(self, color: Color = Color.transparent()):
        self._canvas.clear(color)

    def display(self):
        self._canvas.display()

    def __del__(self):
        self._executor.shutdown(wait=True)
        self.graphics_mgr.clear()
        self.animation_mgr.clear()
        self.particle_mgr.clear()