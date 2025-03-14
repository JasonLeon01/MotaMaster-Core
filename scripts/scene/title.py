from scripts.core.scene import SceneBase
from scripts.core.window import Window
from scripts.core.graphics import Graphics
from PySFBoost import sfGraphics, ResourceMgr

class Scene(SceneBase):
    def __init__(self):
        self.sprite = sfGraphics.Sprite(ResourceMgr.TextureMgr.system("GrassBackground.png"))

        self.window = Window(sfGraphics.IntRect((100, 100, 320, 320)), repeat=True)
        self.window.set_rect(sfGraphics.IntRect((0, 0, 100, 100)))
        super().__init__()

    def on_start(self):
        Graphics.graphics_mgr.add(self.sprite, 0)
        Graphics.graphics_mgr.add(self.window, 0)

    def render_handle(self, delta_time):
        self.window.update(delta_time)
        return super().render_handle(delta_time)

