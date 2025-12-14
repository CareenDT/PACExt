import arcade
from scripts.Class.GameObject import GameObject, Transform, Components

class MenuObject(GameObject):
    def __init__(self, Name, transform = None):
        super().__init__(Name, transform)

        self.add_component(Components.BoxRenderer(color=(0, 0, 0, 150)))
        self.add_component(Components.ScreenRelativeTransform(arcade.get_window(), 0.5, 0.5, 0.35, 1))