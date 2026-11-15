import asyncio
import colorsys
import random
import shutil
import sys
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple, Union

from .config import get_config
from .exceptions import ColorNotSupportedError, ConfigurationError, EffectNotFoundError


class Colors:
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    HIDDEN = "\033[8m"
    STRIKETHROUGH = "\033[9m"

    RESET = "\033[0m"
    RESET_COLOR = "\033[39m"
    RESET_BG = "\033[49m"

    @staticmethod
    def _color(kind: int, r: int, g: int, b: int) -> str:
        r, g, b = (max(0, min(255, int(v))) for v in (r, g, b))
        config = get_config()
        if config.enable_true_color:
            return f"\033[{kind};2;{r};{g};{b}m"
        if config.fallback_to_8bit:
            index = 16 + 36 * round(r / 255 * 5) + 6 * round(g / 255 * 5) + round(b / 255 * 5)
            return f"\033[{kind};5;{index}m"
        raise ColorNotSupportedError("true color is disabled and the 8-bit fallback is turned off")

    @classmethod
    def rgb(cls, r: int, g: int, b: int) -> str:
        return cls._color(38, r, g, b)

    @classmethod
    def bg_rgb(cls, r: int, g: int, b: int) -> str:
        return cls._color(48, r, g, b)

    @classmethod
    def gradient(cls, text: str, start_color: Tuple[int, int, int], end_color: Tuple[int, int, int]) -> str:
        if not text:
            return ""
        r1, g1, b1 = start_color
        r2, g2, b2 = end_color
        parts = []
        for i, char in enumerate(text):
            ratio = i / max(len(text) - 1, 1)
            parts.append(cls.rgb(r1 + (r2 - r1) * ratio, g1 + (g2 - g1) * ratio, b1 + (b2 - b1) * ratio) + char)
        return "".join(parts) + cls.RESET


@dataclass
class ColorTheme:
    primary: str = Colors.CYAN
    secondary: str = Colors.GREEN
    accent: str = Colors.YELLOW
    error: str = Colors.RED
    success: str = Colors.GREEN
    warning: str = Colors.YELLOW
    info: str = Colors.BLUE

    @classmethod
    def dark(cls) -> "ColorTheme":
        return cls(
            primary=Colors.BRIGHT_CYAN,
            secondary=Colors.BRIGHT_GREEN,
            accent=Colors.BRIGHT_YELLOW,
            error=Colors.BRIGHT_RED,
            success=Colors.BRIGHT_GREEN,
            warning=Colors.BRIGHT_YELLOW,
            info=Colors.BRIGHT_BLUE,
        )

    @classmethod
    def light(cls) -> "ColorTheme":
        return cls(
            primary=Colors.BLUE,
            secondary=Colors.GREEN,
            accent=Colors.MAGENTA,
            error=Colors.RED,
            success=Colors.GREEN,
            warning=Colors.YELLOW,
            info=Colors.CYAN,
        )

    @classmethod
    def rainbow(cls) -> "ColorTheme":
        return cls(
            primary=Colors.RED,
            secondary=Colors.YELLOW,
            accent=Colors.GREEN,
            error=Colors.MAGENTA,
            success=Colors.CYAN,
            warning=Colors.YELLOW,
            info=Colors.BLUE,
        )

    @classmethod
    def named(cls, name: str) -> "ColorTheme":
        themes = {"dark": cls.dark, "light": cls.light, "rainbow": cls.rainbow}
        if name not in themes:
            raise ConfigurationError(f"Unknown theme '{name}'. Available themes: {', '.join(themes)}")
        return themes[name]()


ColorLike = Union[str, ColorTheme]


def _paint(color: ColorLike) -> str:
    return color.primary if isinstance(color, ColorTheme) else color


def _write(text: str) -> None:
    sys.stdout.write(text)
    sys.stdout.flush()


async def type_writer(
    text: str,
    speed: Optional[float] = None,
    color: ColorLike = Colors.RESET,
    jitter: Optional[float] = None,
    sound_effect: bool = False,
    on_char: Optional[Callable[[str], None]] = None,
) -> None:
    config = get_config()
    speed = config.default_speed if speed is None else speed
    jitter = config.type_writer_jitter if jitter is None else jitter
    jitter = min(max(jitter, 0.0), 1.0)
    color = _paint(color)

    for char in text:
        _write(f"{color}{char}{Colors.RESET}")
        if sound_effect:
            sys.stderr.write("\a")
            sys.stderr.flush()
        if on_char:
            on_char(char)

        if char in ".,!?;:":
            factor = 3
        elif char == " ":
            factor = 0.5
        elif char == "\n":
            factor = 5
        else:
            factor = 1
        await asyncio.sleep(speed * factor * random.uniform(1 - jitter, 1 + jitter))

    _write("\n")


async def scanner(
    text: str,
    speed: float = 0.08,
    color: ColorLike = Colors.GREEN,
    width: Optional[int] = None,
    bounce: bool = False,
) -> None:
    width = max(1, get_config().scanner_width if width is None else width)
    color = _paint(color)

    positions = list(range(len(text)))
    if bounce:
        positions += positions[-2::-1]

    for pos in positions:
        start = max(0, pos - width // 2)
        end = min(len(text), pos - width // 2 + width)
        _write(f"\r{text[:start]}{Colors.BOLD}{color}{text[start:end]}{Colors.RESET}{text[end:]}")
        await asyncio.sleep(speed)

    _write(f"\r{text}\n")


async def glitch(
    text: str,
    duration: float = 2.0,
    intensity: float = 0.1,
    color: ColorLike = Colors.RED,
    charset: Optional[str] = None,
    preserve_spaces: bool = True,
) -> None:
    charset = get_config().glitch_charset if charset is None else charset
    color = _paint(color)
    loop = asyncio.get_running_loop()
    started = loop.time()

    while True:
        elapsed = loop.time() - started
        if elapsed >= duration:
            break
        current = intensity * (1 - 0.5 * elapsed / duration)

        line = []
        for char in text:
            if preserve_spaces and char == " ":
                line.append(" ")
            elif random.random() < current:
                line.append(random.choice(charset))
            else:
                line.append(char)

        if random.random() < 0.1:
            offset = random.randint(-2, 2)
            if offset > 0:
                line = [" "] * offset + line[:-offset]
            elif offset < 0:
                line = line[-offset:] + [" "] * -offset

        _write(f"\r{color}{''.join(line)}{Colors.RESET}")
        await asyncio.sleep(0.05)

    _write(f"\r{text}\n")


FADE_EFFECTS = ["dots", "fade", "dissolve", "vaporize"]


async def fade_out(
    text: str,
    speed: float = 0.05,
    effect: Optional[str] = None,
    color: ColorLike = Colors.RESET,
) -> None:
    effect = get_config().fade_out_effect if effect is None else effect
    if effect not in FADE_EFFECTS:
        raise EffectNotFoundError(effect, FADE_EFFECTS)
    color = _paint(color)
    chars = list(text)
    order = list(range(len(text)))

    if effect == "dots":
        random.shuffle(order)
        for idx in order:
            chars[idx] = random.choice([".", "·", " ", " "])
            _write(f"\r{color}{''.join(chars)}{Colors.RESET}")
            await asyncio.sleep(speed * random.uniform(0.5, 1.5))

    elif effect == "fade":
        steps = 10
        for step in range(steps, -1, -1):
            shade = 232 + round(23 * step / steps)
            _write(f"\r\033[38;5;{shade}m{text}{Colors.RESET}")
            await asyncio.sleep(speed * 2)

    elif effect == "dissolve":
        random.shuffle(order)
        for idx in order:
            chars[idx] = " "
            _write(f"\r{color}{''.join(chars)}{Colors.RESET}")
            await asyncio.sleep(speed)

    else:
        for step in range(len(text) + 3):
            line = "".join(" " if step - j > 0 else char for j, char in enumerate(text))
            _write(f"\r{color}{line}{Colors.RESET}")
            await asyncio.sleep(speed)

    _write("\r" + " " * len(text) + "\r")


async def progress_bar(
    total: int,
    prefix: str = "",
    suffix: str = "",
    length: int = 30,
    fill: str = "█",
    empty: str = "░",
    color: ColorLike = Colors.GREEN,
    show_percentage: bool = True,
    show_count: bool = True,
    speed: float = 0.1,
) -> None:
    if total <= 0:
        raise ValueError("total must be a positive integer")
    color = _paint(color)

    for i in range(total + 1):
        filled = length * i // total
        bar = fill * filled + empty * (length - filled)

        parts: List[str] = []
        if prefix:
            parts.append(prefix)
        parts.append(f"{color}[{bar}]{Colors.RESET}")
        if show_percentage:
            parts.append(f"{100 * i / total:.1f}%")
        if show_count:
            parts.append(f"({i}/{total})")
        if suffix:
            parts.append(suffix)

        _write("\r" + " ".join(parts))
        if i < total:
            await asyncio.sleep(speed)

    _write("\n")


def _hue_to_rgb(hue: float) -> Tuple[int, int, int]:
    r, g, b = colorsys.hsv_to_rgb(hue % 1.0, 1.0, 1.0)
    return int(r * 255), int(g * 255), int(b * 255)


async def rainbow_text(text: str, speed: float = 0.1, cycle: bool = True) -> None:
    frame = 0
    try:
        while True:
            line = "".join(
                Colors.rgb(*_hue_to_rgb(frame / 60 + i / len(text))) + char
                for i, char in enumerate(text)
            )
            _write(f"\r{line}{Colors.RESET}")
            await asyncio.sleep(speed)
            frame += 1
            if not cycle and frame >= 60:
                break
    finally:
        _write(f"\r{text}\n")


class _Particle:
    def __init__(self, char: str, x: float, y: float):
        self.char = char
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-3, 0)
        self.life = 1.0
        self.decay = random.uniform(0.02, 0.05)

    def step(self) -> None:
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.life -= self.decay


async def particle_explosion(text: str, duration: float = 1.5, particle_count: int = 50) -> None:
    columns, rows = shutil.get_terminal_size()
    visible = [i for i, char in enumerate(text) if char != " "]
    per_char = max(1, particle_count // max(len(visible), 1))
    left = (columns - len(text)) // 2
    particles = [_Particle(text[i], left + i, rows // 2) for i in visible for _ in range(per_char)]

    loop = asyncio.get_running_loop()
    started = loop.time()
    _write("\033[?1049h")
    try:
        while loop.time() - started < duration:
            frame = ["\033[2J"]
            alive = []
            for p in particles:
                p.step()
                if p.life <= 0:
                    continue
                alive.append(p)
                x, y = int(p.x), int(p.y)
                if 0 <= x < columns and 0 <= y < rows:
                    level = int(255 * p.life)
                    shade = Colors.rgb(level, level // 2, max(0, level - 100))
                    frame.append(f"\033[{y + 1};{x + 1}H{shade}{p.char}")
            particles = alive
            frame.append(Colors.RESET)
            _write("".join(frame))
            await asyncio.sleep(0.05)
    finally:
        _write("\033[?1049l")
