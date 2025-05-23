from PySFBoost.sfWindow import *

class GameInput:
    _keys_hash = {}
    _keys_repeat = {}

    _mouse_pressing = [False, False, False, False, False]
    wheel_delta = 0
    focused = True

    @classmethod
    def press(cls, key: Keyboard.Key) -> bool:
        if not cls.focused:
            return False
        return Keyboard.is_key_pressed(key)

    @classmethod
    def trigger(cls, key: Keyboard.Key) -> bool:
        if not cls.focused:
            return False
        if key not in cls._keys_hash:
            cls._keys_hash[key] = False
        pressing = Keyboard.is_key_pressed(key)
        if cls._keys_hash[key] and pressing:
            return False
        if pressing:
            cls._keys_hash[key] = True
            return True
        cls._keys_hash[key] = False
        return False

    @classmethod
    def repeat(cls, key: Keyboard.Key, interval: float, delta_time: float) -> bool:
        if not cls.focused:
            return False
        pressing = Keyboard.is_key_pressed(key)
        if pressing:
            if key not in cls._keys_repeat or cls._keys_repeat[key] <= 0:
                cls._keys_repeat[key] = interval
                return True
            cls._keys_repeat[key] -= delta_time
        else:
            if key in cls._keys_repeat:
                cls._keys_repeat.pop(key)
            if key in cls._keys_hash:
                cls._keys_hash.pop(key)
        return False

    @classmethod
    def left_click(cls) -> bool:
        if not cls.focused:
            return False
        last = cls._mouse_pressing[0]
        cls._mouse_pressing[0] = Mouse.is_button_pressed(Mouse.Button.Left)
        if not last and cls._mouse_pressing[0]:
            return True
        return False

    @classmethod
    def right_click(cls) -> bool:
        if not cls.focused:
            return False
        last = cls._mouse_pressing[1]
        cls._mouse_pressing[1] = Mouse.is_button_pressed(Mouse.Button.Right)
        if not last and cls._mouse_pressing[1]:
            return True
        return False

    @classmethod
    def middle_click(cls) -> bool:
        if not cls.focused:
            return False
        last = cls._mouse_pressing[2]
        cls._mouse_pressing[2] = Mouse.is_button_pressed(Mouse.Button.Middle)
        if not last and cls._mouse_pressing[2]:
            return True
        return False

    @classmethod
    def x1_click(cls) -> bool:
        if not cls.focused:
            return False
        last = cls._mouse_pressing[3]
        cls._mouse_pressing[3] = Mouse.is_button_pressed(Mouse.Button.Extra1)
        if not last and cls._mouse_pressing[3]:
            return True
        return False

    @classmethod
    def x2_click(cls) -> bool:
        if not cls.focused:
            return False
        last = cls._mouse_pressing[4]
        cls._mouse_pressing[4] = Mouse.is_button_pressed(Mouse.Button.Extra2)
        if not last and cls._mouse_pressing[4]:
            return True
        return False

    @classmethod
    def left_press(cls) -> bool:
        if not cls.focused:
            return False
        cls._mouse_pressing[0] = Mouse.is_button_pressed(Mouse.Button.Left)
        return cls._mouse_pressing[0]

    @classmethod
    def right_press(cls) -> bool:
        if not cls.focused:
            return False
        cls._mouse_pressing[1] = Mouse.is_button_pressed(Mouse.Button.Right)
        return cls._mouse_pressing[1]

    @classmethod
    def middle_press(cls) -> bool:
        if not cls.focused:
            return False
        cls._mouse_pressing[2] = Mouse.is_button_pressed(Mouse.Button.Middle)
        return cls._mouse_pressing[2]

    @classmethod
    def x1_press(cls) -> bool:
        if not cls.focused:
            return False
        cls._mouse_pressing[3] = Mouse.is_button_pressed(Mouse.Button.Extra1)
        return cls._mouse_pressing[3]

    @classmethod
    def x2_press(cls) -> bool:
        if not cls.focused:
            return False
        cls._mouse_pressing[4] = Mouse.is_button_pressed(Mouse.Button.Extra2)
        return cls._mouse_pressing[4]

    @classmethod
    def wheel_up(cls) -> bool:
        if not cls.focused:
            return False
        if cls.wheel_delta > 0:
            return True
        return False

    @classmethod
    def wheel_down(cls) -> bool:
        if not cls.focused:
            return False
        if cls.wheel_delta < 0:
            return True
        return False

    @classmethod
    def joystick_press(cls, joystick_id: int, button: int) -> bool:
        if not cls.focused:
            return False
        return Joystick.is_button_pressed(joystick_id, button)
