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
        graphics.Graphics.transition()

        window = system.System.window
        while window.is_open():
            input.WindowInput.clear()
            while True:
                event = window.poll_event()
                if event is None:
                    break
                if event.isClosed():
                    window.close()
                if event.isFocusLost():
                    input.WindowInput.pause()
                if event.isFocusGained():
                    input.WindowInput.resume()
                if event.isTextEntered():
                    input.WindowInput.textEntered = event
                if event.isKeyPressed():
                    input.WindowInput.keyPressed = event
                if event.isKeyReleased():
                    input.WindowInput.keyReleased = event
                if event.isMouseWheelScrolled():
                    input.WindowInput.mouseWheelScrolled = event
                if event.isMouseButtonPressed():
                    input.WindowInput.mouseButtonPressed = event
                if event.isMouseButtonReleased():
                    input.WindowInput.mouseButtonReleased = event
                if event.isMouseMoved():
                    input.WindowInput.mouseMoved = event
                if event.isMouseMovedRaw():
                    input.WindowInput.mouseMovedRaw = event
                if event.isMouseEntered():
                    input.WindowInput.mouseEntered = event
                if event.isMouseLeft():
                    input.WindowInput.mouseLeft = event
                if event.isJoystickButtonPressed():
                    input.WindowInput.joystickButtonPressed = event
                if event.isJoystickButtonReleased():
                    input.WindowInput.joystickButtonReleased = event
                if event.isJoystickMoved():
                    input.WindowInput.joystickMoved = event
                if event.isJoystickConnected():
                    input.WindowInput.joystickConnected = event
                if event.isJoystickDisconnected():
                    input.WindowInput.joystickDisconnected = event
                if event.isTouchBegan():
                    input.WindowInput.touchBegan = event
                if event.isTouchMoved():
                    input.WindowInput.touchMoved = event
                if event.isTouchEnded():
                    input.WindowInput.touchEnded = event
                if input.WindowInput.is_paused():
                    input.WindowInput.clear()

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
        self.on_late_update(delta_time)
