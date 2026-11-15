import asyncio
import os
import sys
from typing import Any, Awaitable, Callable, Optional, Sequence, Set, Union

from .animators import SpinnerAnimator
from .config import get_config
from .effects import ColorTheme
from .exceptions import AnimationError, TerminalError

HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"


def _enable_ansi() -> None:
    if os.name != "nt":
        return
    import ctypes

    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)
    mode = ctypes.c_ulong()
    if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)


class AnimationController:
    def __init__(self, limit: Optional[int] = None):
        self.limit = get_config().max_concurrent_animations if limit is None else limit
        self._tasks: Set[asyncio.Task] = set()

    @property
    def active(self) -> int:
        return len(self._tasks)

    def spawn(self, coroutine: Awaitable[Any]) -> asyncio.Task:
        if len(self._tasks) >= self.limit:
            coroutine.close()
            raise AnimationError(f"limit of {self.limit} concurrent animations reached")
        task = asyncio.ensure_future(coroutine)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task

    async def cancel_all(self) -> None:
        tasks = list(self._tasks)
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


class Termimato:
    def __init__(
        self,
        theme: Optional[Union[str, ColorTheme]] = None,
        controller: Optional[AnimationController] = None,
    ):
        if not isinstance(theme, ColorTheme):
            theme = ColorTheme.named(theme or get_config().default_theme)
        self.theme = theme
        self.controller = controller or AnimationController()

    async def __aenter__(self) -> "Termimato":
        config = get_config()
        if config.check_terminal_support and not sys.stdout.isatty():
            raise TerminalError("stdout is not a terminal")
        _enable_ansi()
        if config.auto_restore_cursor:
            sys.stdout.write(HIDE_CURSOR)
            sys.stdout.flush()
        return self

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        await self.controller.cancel_all()
        if get_config().auto_restore_cursor:
            sys.stdout.write(SHOW_CURSOR)
            sys.stdout.flush()

    async def play(self, func: Callable[..., Awaitable[None]], /, *args: Any, **kwargs: Any) -> None:
        try:
            await func(*args, **kwargs)
        except (asyncio.CancelledError, AnimationError):
            raise
        except Exception as e:
            raise AnimationError(str(e), getattr(func, "__name__", None)) from e

    async def start_spinner(
        self,
        label: str = "Loading",
        color: Optional[str] = None,
        frames: Optional[Sequence[str]] = None,
        interval: float = 0.1,
    ) -> asyncio.Task:
        animator = SpinnerAnimator(frames, label, color or self.theme.primary, interval)
        return self.controller.spawn(animator.start())
