import arcade
from typing import List, Type, Dict, Optional, Any

class Component:
    """Base class for all components"""
    def __init__(self, game_object: 'GameObject' = None):
        self.game_object = game_object
        
    def start(self):
        """[ABSTRACT] called when the component is added /// Setup function"""
        pass
    
    def update(self, delta_time: float):
        """[ABSTRACT] called on gameobject update"""
        pass
    
    def on_draw(self):
        """[ABSTRACT] called on gameobject draw"""
        pass
    
    def destroy(self):
        """[ABSTRACT] called when the component is destroyed /// Cleanup function"""
        pass

class GameObject():
    def __init__(self, Name, transform: Transform = None):

        self.Name = Name
        self.transform = transform

        self.components: Dict[Type[Component], List[Component]] = {}

    # Components
    def add_component(self, component: Component) -> Component:

        """Add a component to this GameObject"""

        component.game_object = self
        comp_type = type(component)
        if comp_type not in self.components: # Null safety
            self.components[comp_type] = []
        
        self.components[comp_type].append(component)

        component.start()

        return component
    
    def get_component(self, component_type: Type[Component]) -> Optional[Component]:

        """Get the first component of specified type"""

        if component_type in self.components and self.components[component_type]:
            return self.components[component_type][0]

        return None
    
    def get_components(self, component_type: Type[Component]) -> List[Component]:

        """Get all components of specified type"""

        return self.components.get(component_type, [])
    
    def remove_component(self, component: Component):
        """Remove a specific component"""

        comp_type = type(component)

        if comp_type in self.components and component in self.components[comp_type]:
            component.destroy()
            self.components[comp_type].remove(component)
            
            if not self.components[comp_type]: # Clean up
                del self.components[comp_type]
    
    def remove_all_components(self):

        """Remove all components from this GameObject"""

        for comp_list in self.components.values():
            for component in comp_list:
                component.destroy()
        self.components.clear()
    
    def has_component(self, component_type: Type[Component]) -> bool:

        """Check if GameObject has at least one component of specified type"""

        return component_type in self.components
    
    def get_all_components(self) -> List[Component]:

        """Get list of all components"""

        all_components = []

        for comp_list in self.components.values():
            all_components.extend(comp_list)
        return all_components
    
    # General
    
    def update(self, delta_time):

        """Update all components"""

        for comp_list in self.components.values():
            for component in comp_list:
                component.update(delta_time)
    
    def draw(self):

        """Draw the GameObject and its components"""
        # Call on_draw for all components
        for comp_list in self.components.values():
            for component in comp_list:
                component.on_draw()

    def __repr__(self):
        return f"Name: {self.Name}; Gameobject(Position: {self.center_x, self.center_y};)"

class Transform:
    """Transform component"""
    def __init__(self, x: float = 0.0, y: float = 0.0, 
                 rotation: float = 0.0, scale: float = 1.0):
        
        self.position = arcade.Vec2(x, y)
        self.rotation = rotation
        self.scale = arcade.Vec2(scale, scale)

class ScreenRelativeTransform(Component):
    def __init__(self, Subject: arcade.Window | GameObject, x = 0, y = 0, scale_x: float = 1, scale_y: float = 1, game_object = None):
        super().__init__(game_object)

        self.RelativePosX = x
        self.RelativePosY = y

        self.RelativeTo = Subject

        self.RelativeScaleX = scale_x
        self.RelativeScaleY = scale_y

    def update(self, delta_time):
        self.game_object.transform.position = arcade.Vec2(self.RelativePosX * self.RelativeTo.width,self.RelativePosY * self.RelativeTo.height)
        self.game_object.transform.scale = arcade.Vec2(self.RelativeScaleX * self.RelativeTo.width, self.RelativeScaleY * self.RelativeTo.height)


class SpriteRendererComponent(Component):
    """Sprite component"""
    
    def __init__(self, image_path, scale=1.0, animation: FrameAnimation = None):
        super().__init__()
        self.batch: arcade.SpriteList = None

        self.sprite: arcade.Sprite = arcade.Sprite(image_path, scale)

        self.Animation: FrameAnimation = animation
    
    def start(self):
        if self.game_object and self.game_object.transform:
            self.sync_with_transform()

    def set_Animation(self, anim: FrameAnimation):
        self.Animation = anim
        anim.Bind(self)

    def sync_with_transform(self):
        """Update sprite to match GameObject's transform"""
        if self.game_object and self.game_object.transform:
            t = self.game_object.transform
            
            # Update
            self.sprite.center_x = t.position.x
            self.sprite.center_y = t.position.y
            self.sprite.angle = t.rotation

            self.sprite.scale_x = t.scale.x / self.sprite.texture.width
            self.sprite.scale_y = t.scale.y / self.sprite.texture.height
    
    def update(self, delta_time):
        self.sync_with_transform()
        self.sprite.update()

        if self.Animation:
            if self.Animation.IsPlaying:
                self.Animation.on_update(delta_time)
    
    def on_draw(self):
        if not self.batch:
            self.sprite.draw()
    
    def add_to_batch(self, sprite_list):
        """Add to SpriteList for batch rendering"""
        if self.batch and self.sprite in self.batch:
            self.batch.remove(self.sprite)
        self.batch = sprite_list
        sprite_list.append(self.sprite)


class FrameAnimation:
    def __init__(self, Textures: List[str], FPS:int = 2, PlayOnStart:bool = False, IsLooped:bool = False):
        self.TextureList = [arcade.load_texture(T) for T in Textures]

        self.IsLooped = IsLooped
        self.IsPlaying = PlayOnStart

        self.FPS = FPS
        self.Sprite: SpriteRendererComponent = None

        self._elapsed = 0

        self._index = 0

    def Bind(self, To: SpriteRendererComponent):
        self.Sprite = To

    def _next(self):
        if self.Sprite:
            self.Sprite.sprite.texture = self.TextureList[(int)(self._index)]

    def on_update(self, delta_time):
        if self.Sprite:
            self._elapsed += delta_time
            if self._elapsed >= 1 / self.FPS:
                self._index = (self._index + (self._elapsed / (1 / self.FPS))) % len(self.TextureList)
                self._next()
                self._elapsed %= 1 / self.FPS

class AspectRatioComponent(Component):
    def __init__(self, Ratio:float = 1, RelativeToX:bool = True, game_object: 'GameObject' = None):
        self.game_object = game_object
        self.RelativeToX = RelativeToX
        self.ratio = Ratio
    
    def update(self, delta_time):
        if self.RelativeToX:
            self.game_object.transform.scale = arcade.Vec2(self.game_object.transform.scale.x, self.game_object.transform.scale.x * self.ratio)
        else:
            self.game_object.transform.scale = arcade.Vec2(self.game_object.transform.scale.y * self.ratio, self.game_object.transform.scale.y)

class BoxRenderer(Component):
    """Box drawing"""

    def __init__(self, color, game_object = None):
        self.game_object = game_object
        self.color = color

    def on_draw(self):
        if not self.game_object or not self.game_object.transform:
            return
            
        t = self.game_object.transform

        x = t.position.x
        y = t.position.y
        width = t.scale.x
        height = t.scale.y

        arcade.draw_rect_filled(
            arcade.rect.XYWH(x, y, width, height),
            self.color
        )

class Components:
    AspectRatio = AspectRatioComponent
    ScreenRelativeTransform = ScreenRelativeTransform
    SpriteRenderer = SpriteRendererComponent
    BoxRenderer = BoxRenderer