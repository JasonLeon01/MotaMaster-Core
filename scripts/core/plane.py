from PySFBoost import sfGraphics, sfSystem

class Plane(sfGraphics.Sprite):
    def __init__(self, texture: sfGraphics.Texture, size: sfSystem.Vector2i):
        super().__init__(texture)
        texture.set_repeated(True)
        self.set_texture_rect(sfGraphics.IntRect(sfSystem.Vector2i(0, 0), size))
