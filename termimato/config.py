import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Optional, Union

from .exceptions import ConfigurationError


@dataclass
class TermimatoConfig:
    auto_restore_cursor: bool = True
    check_terminal_support: bool = True
    default_speed: float = 0.05
    max_concurrent_animations: int = 10
    enable_true_color: bool = True
    fallback_to_8bit: bool = True
    default_theme: str = "dark"
    type_writer_jitter: float = 0.5
    scanner_width: int = 3
    glitch_charset: str = "X#&%$@*!?<>/\\"
    fade_out_effect: str = "dots"


DEFAULT_CONFIG = TermimatoConfig()

_current_config: Optional[TermimatoConfig] = None


def _default_path() -> Path:
    return Path.home() / ".config" / "termimato" / "config.json"


def get_config() -> TermimatoConfig:
    global _current_config
    if _current_config is None:
        try:
            _current_config = load_config()
        except ConfigurationError:
            _current_config = TermimatoConfig()
    return _current_config


def set_config(config: TermimatoConfig) -> None:
    global _current_config
    _current_config = config


def update_config(**kwargs) -> None:
    config = get_config()
    for key, value in kwargs.items():
        if not hasattr(config, key):
            raise ConfigurationError(f"Unknown configuration option: {key}")
        setattr(config, key, value)


def reset_config() -> None:
    global _current_config
    _current_config = TermimatoConfig()


def save_config(path: Optional[Union[str, Path]] = None) -> Path:
    target = Path(path) if path else _default_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        json.dump(asdict(get_config()), f, indent=2, ensure_ascii=False)
    return target


def load_config(path: Optional[Union[str, Path]] = None) -> TermimatoConfig:
    source = Path(path) if path else _default_path()
    if not source.exists():
        return TermimatoConfig()
    try:
        with open(source, "r", encoding="utf-8") as f:
            data = json.load(f)
        known = {f.name for f in fields(TermimatoConfig)}
        return TermimatoConfig(**{k: v for k, v in data.items() if k in known})
    except (json.JSONDecodeError, TypeError, AttributeError) as e:
        raise ConfigurationError(f"Failed to load configuration: {e}") from e
