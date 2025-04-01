from functools import partial
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from PySFBoost.sfWindow import Event
from PySFBoost.Time import TimeMgr
from PySFBoost.ResourceMgr import AudioMgr
from .inputs import GameInput

class SceneBase:
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers = 2)
        self._audio_interval = 0

    def main(self):
        self.on_start()

        from .system import System
        from .graphics import Graphics
        Graphics.transition()

        window = System.window
        while window.is_open():
            GameInput.wheel_delta = 0
            event: Event = None
            try:
                while True:
                    event = window.poll_event()
                    if event is None:
                        break
                    if event.isClosed():
                        window.close()
                    if event.isFocusLost():
                        GameInput.focused = False
                    if event.isFocusGained():
                        GameInput.focused = True
                    if event.isMouseWheelScrolled():
                        wheel_event = event.getIfMouseWheelScrolled()
                        if wheel_event is not None:
                            GameInput.wheel_delta = wheel_event.delta
            except Exception as e:
                logging.error("Window execution failed: %s\n%s", e, traceback.format_exc())

            TimeMgr.update()
            delta_time = TimeMgr.get_delta_time().as_seconds()
            self.update(delta_time)

            if System.current_scene != self:
                break

        Graphics.freeze()
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
        from .graphics import Graphics
        Graphics.animation_mgr.update(delta_time)
        Graphics.particle_mgr.update(delta_time)
        Graphics.video_mgr.update(delta_time)
        Graphics.update(delta_time)

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

        from .system import System
        System.window.display()
        self.on_late_update(delta_time)
