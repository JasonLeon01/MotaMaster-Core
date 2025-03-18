from functools import partial
import logging
import traceback
from . import graphics, method, system, inputs
import PySFBoost.Time as Time
from PySFBoost.ResourceMgr import AudioMgr
from concurrent.futures import ThreadPoolExecutor, as_completed

class SceneBase:
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers = 2)
        self._audio_interval = 0

    def main(self):
        self.on_start()
        graphics.Graphics.transition()

        window = system.System.window
        inputs.GameInput.wheel_delta = 0
        while window.is_open():
            while True:
                event = window.poll_event()
                if event is None:
                    break
                if event.isClosed():
                    window.close()
                # if event.isMouseWheelScrolled():
                #     wheel_event = event.getIfMouseWheelScrolled()
                #     inputs.GameInput.wheel_delta = wheel_event.delta

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
        if self._audio_interval < 10:
            self._audio_interval += delta_time
            return
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
