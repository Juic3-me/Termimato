import asyncio
import itertools
import sys
import time
from dataclasses import dataclass
from enum import Enum
from typing import Awaitable, Callable, Optional, Sequence

from .effects import Colors
from .exceptions import AnimationError

SPINNER_FRAMES = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")


def _write(text: str) -> None:
    sys.stdout.write(text)
    sys.stdout.flush()


class AnimationState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


@dataclass
class AnimationMetrics:
    start_time: float = 0.0
    end_time: float = 0.0
    frame_count: int = 0

    @property
    def duration(self) -> float:
        if self.end_time > 0 and self.start_time > 0:
            return self.end_time - self.start_time
        return 0.0

    @property
    def fps(self) -> float:
        if self.duration > 0 and self.frame_count > 0:
            return self.frame_count / self.duration
        return 0.0


class BaseAnimator:
    def __init__(self, name: str = "Animator"):
        self.name = name
        self.state = AnimationState.IDLE
        self.metrics = AnimationMetrics()
        self._task: Optional[asyncio.Task] = None
        self._stop_event: Optional[asyncio.Event] = None

    async def start(self) -> None:
        if self.state in (AnimationState.RUNNING, AnimationState.PAUSED):
            raise AnimationError(f"{self.name} is already running")

        self._stop_event = asyncio.Event()
        self.state = AnimationState.RUNNING
        self.metrics = AnimationMetrics(start_time=time.time())
        self._task = asyncio.create_task(self._run())

        try:
            await self._task
        except asyncio.CancelledError:
            self.state = AnimationState.CANCELLED
            if not self._stop_event.is_set():
                raise
        except Exception as e:
            self.state = AnimationState.ERROR
            raise AnimationError(f"{self.name} failed: {e}") from e
        else:
            self.state = AnimationState.COMPLETED
        finally:
            self.metrics.end_time = time.time()

    async def stop(self) -> None:
        if self._task is None or self._task.done():
            return
        self._stop_event.set()
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass

    async def pause(self) -> None:
        if self.state is AnimationState.RUNNING:
            self.state = AnimationState.PAUSED

    async def resume(self) -> None:
        if self.state is AnimationState.PAUSED:
            self.state = AnimationState.RUNNING

    async def _run(self) -> None:
        raise NotImplementedError

    async def _wait(self, delay: float) -> bool:
        try:
            await asyncio.wait_for(self._stop_event.wait(), timeout=delay)
            return True
        except asyncio.TimeoutError:
            return False

    def _record_frame(self) -> None:
        self.metrics.frame_count += 1

    def get_stats(self) -> dict:
        return {
            "name": self.name,
            "state": self.state.value,
            "duration": self.metrics.duration,
            "frames": self.metrics.frame_count,
            "fps": self.metrics.fps,
        }


class SpinnerAnimator(BaseAnimator):
    def __init__(
        self,
        frames: Optional[Sequence[str]] = None,
        label: str = "Loading",
        color: str = Colors.CYAN,
        interval: float = 0.1,
    ):
        super().__init__(name=f"Spinner-{label}")
        self.frames = tuple(frames) if frames else SPINNER_FRAMES
        self.label = label
        self.color = color
        self.interval = interval

    async def _run(self) -> None:
        try:
            for frame in itertools.cycle(self.frames):
                if self.state is AnimationState.PAUSED:
                    if await self._wait(0.1):
                        break
                    continue
                self._render_frame(frame)
                self._record_frame()
                if await self._wait(self.interval):
                    break
        finally:
            _write("\r\033[K")

    def _render_frame(self, frame: str) -> None:
        _write(f"\r{self.color}{frame}{Colors.RESET} {self.label}\033[K")


class ProgressAnimator(BaseAnimator):
    def __init__(
        self,
        total: int = 100,
        label: str = "Progress",
        color: str = Colors.CYAN,
        width: int = 40,
        show_percentage: bool = True,
        show_eta: bool = True,
    ):
        super().__init__(name=f"ProgressBar-{label}")
        self.total = total
        self.current = 0
        self.label = label
        self.color = color
        self.width = width
        self.show_percentage = show_percentage
        self.show_eta = show_eta

    def update(self, value: int) -> None:
        self.current = min(max(value, 0), self.total)

    def increment(self, amount: int = 1) -> None:
        self.update(self.current + amount)

    async def _run(self) -> None:
        while True:
            if self.state is AnimationState.PAUSED:
                if await self._wait(0.1):
                    break
                continue
            self._render_frame()
            self._record_frame()
            if self.current >= self.total:
                break
            if await self._wait(0.05):
                break

    def _render_frame(self) -> None:
        percent = self.current / self.total if self.total > 0 else 1.0
        filled = int(self.width * percent)
        bar = "█" * filled + "░" * (self.width - filled)

        eta = ""
        if self.show_eta and self.current > 0 and self.metrics.start_time:
            elapsed = time.time() - self.metrics.start_time
            if elapsed > 0:
                eta = f" ETA: {elapsed / self.current * (self.total - self.current):.1f}s"

        percentage = f" {percent:.1%}" if self.show_percentage else ""
        _write(f"\r{self.color}{self.label}: [{bar}]{percentage}{eta}{Colors.RESET}\033[K")

    async def complete(self) -> None:
        self.current = self.total
        self._render_frame()
        started = self.metrics.start_time
        elapsed = self.metrics.duration or (time.time() - started if started else 0.0)
        _write(f"\n{Colors.GREEN}✓ {self.label} completed in {elapsed:.2f}s{Colors.RESET}\n")


class CountdownAnimator(BaseAnimator):
    def __init__(
        self,
        seconds: int = 10,
        format_string: str = "{seconds:02d}",
        color: str = Colors.BRIGHT_RED,
        final_message: str = "GO!",
    ):
        super().__init__(name=f"Countdown-{seconds}s")
        self.seconds = seconds
        self.format_string = format_string
        self.color = color
        self.final_message = final_message
        self.current_second = seconds

    async def _run(self) -> None:
        self.current_second = self.seconds
        while self.current_second > 0:
            if self.state is AnimationState.PAUSED:
                if await self._wait(0.1):
                    return
                continue
            self._render_frame()
            self._record_frame()
            if await self._wait(1):
                return
            self.current_second -= 1
        _write(f"\r{Colors.BRIGHT_GREEN}{self.final_message}{Colors.RESET}\033[K\n")

    def _render_frame(self) -> None:
        total = self.current_second
        text = self.format_string.format(
            seconds=total,
            minutes=total % 3600 // 60,
            hours=total // 3600,
            formatted_seconds=f"{total % 60:02d}",
            formatted_minutes=f"{total % 3600 // 60:02d}",
            formatted_hours=f"{total // 3600:02d}",
        )
        _write(f"\r{self.color}{text}{Colors.RESET}\033[K")


class TextAnimator(BaseAnimator):
    def __init__(self, text: str, effect_func: Callable[[str], Awaitable[None]], effect_name: str = "TextEffect"):
        super().__init__(name=f"{effect_name}-Animator")
        self.text = text
        self.effect_func = effect_func
        self.effect_name = effect_name

    async def _run(self) -> None:
        await self.effect_func(self.text)
