from functools import partial
import logging
import traceback
from . import graphics, method, system, input
import PySFBoost.Time as Time
from PySFBoost.ResourceMgr import AudioMgr
from concurrent.futures import ThreadPoolExecutor, as_completed

class SceneBase:
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers = 2)

    def main(self):
        self.on_start()

        window = system.System.window
        while window.is_open():
            input.Input.clear()
            while True:
                event = window.poll_event()
                if event is None:
                    break
                if event.isClosed():
                    window.close()
                if event.isFocusLost():
                    input.Input.pause()
                if event.isFocusGained():
                    input.Input.resume()
                if event.isTextEntered():
                    input.Input.textEntered = event
                if event.isKeyPressed():
                    input.Input.keyPressed = event
                if event.isKeyReleased():
                    input.Input.keyReleased = event
                if event.isMouseWheelScrolled():
                    input.Input.mouseWheelScrolled = event
                if event.isMouseButtonPressed():
                    input.Input.mouseButtonPressed = event
                if event.isMouseButtonReleased():
                    input.Input.mouseButtonReleased = event
                if event.isMouseMoved():
                    input.Input.mouseMoved = event
                if event.isMouseMovedRaw():
                    input.Input.mouseMovedRaw = event
                if event.isMouseEntered():
                    input.Input.mouseEntered = event
                if event.isMouseLeft():
                    input.Input.mouseLeft = event
                if event.isJoystickButtonPressed():
                    input.Input.joystickButtonPressed = event
                if event.isJoystickButtonReleased():
                    input.Input.joystickButtonReleased = event
                if event.isJoystickMoved():
                    input.Input.joystickMoved = event
                if event.isJoystickConnected():
                    input.Input.joystickConnected = event
                if event.isJoystickDisconnected():
                    input.Input.joystickDisconnected = event
                if event.isTouchBegan():
                    input.Input.touchBegan = event
                if event.isTouchMoved():
                    input.Input.touchMoved = event
                if event.isTouchEnded():
                    input.Input.touchEnded = event
                if input.Input.is_paused():
                    input.Input.clear()

            Time.TimeMgr.update()
            delta_time = Time.TimeMgr.get_delta_time().as_seconds()
            self.update(delta_time)

            if system.System.current_scene != self:
                break

        self.on_stop()

    def on_start(self):
        pass

    def on_update(self, delta_time: float):
        pass

    def on_late_update(self, delta_time: float):
        pass

    def on_stop(self):
        self._executor.shutdown(wait=True)

    def logic_handle(self, delta_time: float):
        pass

    def render_handle(self, delta_time: float):
        graphics.Graphics.animation_mgr.update(delta_time)
        graphics.Graphics.particle_mgr.update(delta_time)
        graphics.Graphics.update(delta_time)

    def audio_handle(self, delta_time: float):
        AudioMgr.update()

    def update(self, delta_time: float):
        self.on_update(delta_time)

        logical_future = self._executor.submit(partial(self.logic_handle, delta_time))
        audio_future = self._executor.submit(partial(self.audio_handle, delta_time))
        futures = [logical_future, audio_future]

        self.render_handle(delta_time)

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.error("Thread execution failed: %s\n%s", e, traceback.format_exc())

        system.System.window.display()
        print("fps:", 1.0 / delta_time)
        self.on_late_update(delta_time)
