from PySFBoost.sfGraphics import IntRect, Sprite, Texture
from PySFBoost.sfSystem import Vector2i

class Plane(Sprite):
    def __init__(self, texture: Texture, size: Vector2i):
        super().__init__(texture)
        texture.set_repeated(True)
        self.set_texture_rect(IntRect(Vector2i(0, 0), size))
