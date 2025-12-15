import arcade
from scripts.globals import HEIGHT, WIDTH
from scripts.Menu import MenuObject
from scripts.Class.GameObject import GameObject, Transform, Components

class Game(arcade.Window):
    def __init__(self, title: str):
        super().__init__(WIDTH, HEIGHT, title, resizable=True, antialiasing=False)
        self.background_color = arcade.color.WHITE
        self.bg_texture = arcade.load_texture(
            "assets/images/BG.jpg"
        )

    def setup(self):
        self._time = 0

        self.game_objects: list[GameObject] = []

        self.Object_Batch = arcade.SpriteList()

        self.Ball = GameObject("Ball", Transform(0,0))
        self.Ball.add_component(Components.SpriteRenderer("assets/images/RedBall.png",1)).add_to_batch(self.Object_Batch)
        self.Ball.add_component(Components.ScreenRelativeTransform(self,0.5,0.5,1,1))

        self.Ball.add_component(Components.AspectRatio())

        self.Menu = MenuObject("Menu", Transform(150, 150, scale = 100))

        self.game_objects.append(self.Ball)
        self.game_objects.append(self.Menu)
        self.keys_pressed = set()

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(
            self.bg_texture,
            arcade.rect.XYWH( 
                self.width // 2,
                self.height // 2,
                self.width,
                self.height,
            ),
        )
        self.Object_Batch.draw(pixelated=True)

        for obj in self.game_objects:
            obj.draw()
     
    def on_update(self, delta_time):
        if arcade.key.SPACE in self.keys_pressed:
            self.Ball.transform.scale += arcade.Vec2(2 * delta_time,2 * delta_time)

        for obj in self.game_objects:
            obj.update(delta_time)
    
    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)


def main():
    game = Game("Synth pool")
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()