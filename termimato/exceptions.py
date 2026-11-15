from typing import List, Optional


class TermimatoError(Exception):
    pass


class AnimationError(TermimatoError):
    def __init__(self, message: str, effect_name: Optional[str] = None):
        self.effect_name = effect_name
        where = f" in {effect_name}" if effect_name else ""
        super().__init__(f"Animation error{where}: {message}")


class ConfigurationError(TermimatoError):
    pass


class EffectNotFoundError(TermimatoError):
    def __init__(self, effect_name: str, available: Optional[List[str]] = None):
        text = f"Effect '{effect_name}' not found."
        if available:
            text += " Available effects: " + ", ".join(available)
        super().__init__(text)


class TerminalError(TermimatoError):
    pass


class ColorError(TermimatoError):
    pass


class ColorNotSupportedError(ColorError):
    pass
