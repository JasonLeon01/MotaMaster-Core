from PySFBoost import sfWindow

class Input:
    textEntered: sfWindow.Event.TextEntered = None
    keyPressed: sfWindow.Event.KeyPressed = None
    keyReleased: sfWindow.Event.KeyReleased = None
    mouseWheelScrolled: sfWindow.Event.MouseWheelScrolled = None
    mouseButtonPressed: sfWindow.Event.MouseButtonPressed = None
    mouseButtonReleased: sfWindow.Event.MouseButtonReleased = None
    mouseMoved: sfWindow.Event.MouseMoved = None
    mouseMovedRaw: sfWindow.Event.MouseMovedRaw = None
    mouseEntered: sfWindow.Event.MouseEntered = None
    mouseLeft: sfWindow.Event.MouseLeft = None
    joystickButtonPressed: sfWindow.Event.JoystickButtonPressed = None
    joystickButtonReleased: sfWindow.Event.JoystickButtonReleased = None
    joystickMoved: sfWindow.Event.JoystickMoved = None
    joystickConnected: sfWindow.Event.JoystickConnected = None
    joystickDisconnected: sfWindow.Event.JoystickDisconnected = None
    touchBegan: sfWindow.Event.TouchBegan = None
    touchMoved: sfWindow.Event.TouchMoved = None
    touchEnded: sfWindow.Event.TouchEnded = None

    _paused = False

    @classmethod
    def clear(cls):
        for key in vars(cls):
            if not key.startswith('_') and not callable(getattr(cls, key)):
                setattr(cls, key, None)

    @classmethod
    def pause(cls):
        cls._paused = True

    @classmethod
    def resume(cls):
        cls._paused = False

    @classmethod
    def is_paused(cls):
        return cls._paused

    @classmethod
    def any_event(cls):
        return any([getattr(cls, key) is not None for key in vars(cls) if not key.startswith('__')])