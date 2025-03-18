from functools import partial
import traceback
from PySFBoost import Animation, Particle, sfGraphics
from scripts.core.graphics import GraphicsMgr
from concurrent.futures import ThreadPoolExecutor

class Viewport(sfGraphics.Sprite):
    def __init__(self, rect: sfGraphics.IntRect):
        self.graphics_mgr = GraphicsMgr()
        self.animation_mgr = Animation.AnimationMgr()
        self.particle_mgr = Particle.ParticleMgr()
        self._canvas = sfGraphics.RenderTexture(rect.size.to_uint())
        self._executor = ThreadPoolExecutor(max_workers = 1)

        super().__init__(self._canvas.get_texture())
        self.set_position(rect.position.to_float())

    def update(self, delta_time: float):
        self._canvas.clear(sfGraphics.Color.transparent())
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

    def clear(self, color: sfGraphics.Color = sfGraphics.Color.transparent()):
        self._canvas.clear(color)

    def display(self):
        self._canvas.display()

    def __del__(self):
        self._executor.shutdown(wait=True)
        self.graphics_mgr.clear()
        self.animation_mgr.clear()
        self.particle_mgr.clear()