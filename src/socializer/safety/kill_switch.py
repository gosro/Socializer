from __future__ import annotations
import os


class KillSwitch:
    def __init__(self, data_dir: str):
        os.makedirs(data_dir, exist_ok=True)
        self._kill = os.path.join(data_dir, "KILL")
        self._pause = os.path.join(data_dir, "PAUSE")

    def engage(self) -> None:
        open(self._kill, "w").close()

    def release(self) -> None:
        if os.path.exists(self._kill):
            os.remove(self._kill)

    def is_engaged(self) -> bool:
        return os.path.exists(self._kill)

    def pause(self) -> None:
        open(self._pause, "w").close()

    def resume(self) -> None:
        if os.path.exists(self._pause):
            os.remove(self._pause)

    def is_paused(self) -> bool:
        return os.path.exists(self._pause)
