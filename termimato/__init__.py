from .animators import (
    AnimationMetrics,
    AnimationState,
    BaseAnimator,
    CountdownAnimator,
    ProgressAnimator,
    SpinnerAnimator,
    TextAnimator,
)
from .config import (
    DEFAULT_CONFIG,
    TermimatoConfig,
    get_config,
    load_config,
    reset_config,
    save_config,
    set_config,
    update_config,
)
from .core import AnimationController, Termimato
from .effects import (
    ColorTheme,
    Colors,
    fade_out,
    glitch,
    particle_explosion,
    progress_bar,
    rainbow_text,
    scanner,
    type_writer,
)
from .exceptions import (
    AnimationError,
    ColorError,
    ColorNotSupportedError,
    ConfigurationError,
    EffectNotFoundError,
    TerminalError,
    TermimatoError,
)

__version__ = "2.0.1"
__author__ = "Mint"
__license__ = "MIT"

__all__ = [
    "Termimato",
    "AnimationController",
    "type_writer",
    "scanner",
    "glitch",
    "fade_out",
    "progress_bar",
    "rainbow_text",
    "particle_explosion",
    "Colors",
    "ColorTheme",
    "BaseAnimator",
    "SpinnerAnimator",
    "ProgressAnimator",
    "CountdownAnimator",
    "TextAnimator",
    "AnimationState",
    "AnimationMetrics",
    "TermimatoConfig",
    "DEFAULT_CONFIG",
    "get_config",
    "set_config",
    "update_config",
    "reset_config",
    "save_config",
    "load_config",
    "TermimatoError",
    "AnimationError",
    "ConfigurationError",
    "EffectNotFoundError",
    "TerminalError",
    "ColorError",
    "ColorNotSupportedError",
]
