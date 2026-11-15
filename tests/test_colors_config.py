import json
import tempfile
import unittest
from pathlib import Path

from termimato import (
    ColorNotSupportedError,
    ColorTheme,
    Colors,
    ConfigurationError,
    TermimatoConfig,
    get_config,
    load_config,
    save_config,
    set_config,
    update_config,
)
from termimato.effects import _hue_to_rgb

from .helpers import OutputTestCase


class ColorsTest(OutputTestCase):
    def test_true_color(self):
        self.assertEqual(Colors.rgb(1, 2, 3), "\033[38;2;1;2;3m")
        self.assertEqual(Colors.bg_rgb(1, 2, 3), "\033[48;2;1;2;3m")

    def test_values_are_clamped(self):
        self.assertEqual(Colors.rgb(-5, 300, 0), "\033[38;2;0;255;0m")

    def test_eight_bit_fallback(self):
        set_config(TermimatoConfig(enable_true_color=False))
        self.assertEqual(Colors.rgb(255, 0, 0), "\033[38;5;196m")

    def test_colors_unavailable(self):
        set_config(TermimatoConfig(enable_true_color=False, fallback_to_8bit=False))
        with self.assertRaises(ColorNotSupportedError):
            Colors.rgb(1, 2, 3)

    def test_gradient_ends(self):
        text = Colors.gradient("ab", (0, 0, 0), (255, 255, 255))
        self.assertTrue(text.startswith("\033[38;2;0;0;0ma"))
        self.assertIn("\033[38;2;255;255;255mb", text)
        self.assertEqual(Colors.gradient("", (0, 0, 0), (1, 1, 1)), "")

    def test_hue_is_not_black(self):
        self.assertEqual(_hue_to_rgb(0), (255, 0, 0))
        self.assertEqual(_hue_to_rgb(1 / 3), (0, 255, 0))
        self.assertEqual(_hue_to_rgb(2 / 3), (0, 0, 255))

    def test_named_themes(self):
        self.assertEqual(ColorTheme.named("light"), ColorTheme.light())
        with self.assertRaises(ConfigurationError):
            ColorTheme.named("neon")


class ConfigTest(OutputTestCase):
    def test_round_trip(self):
        update_config(default_speed=0.2, scanner_width=5)
        with tempfile.TemporaryDirectory() as folder:
            path = save_config(Path(folder) / "nested" / "config.json")
            loaded = load_config(path)
        self.assertEqual(loaded.default_speed, 0.2)
        self.assertEqual(loaded.scanner_width, 5)

    def test_unknown_keys_are_ignored(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.json"
            path.write_text(json.dumps({"default_speed": 0.3, "removed_option": 1}))
            self.assertEqual(load_config(path).default_speed, 0.3)

    def test_broken_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.json"
            path.write_text("{oops")
            with self.assertRaises(ConfigurationError):
                load_config(path)

    def test_missing_file_gives_defaults(self):
        self.assertEqual(load_config("/nonexistent/config.json"), TermimatoConfig())

    def test_update_unknown_option(self):
        with self.assertRaises(ConfigurationError):
            update_config(no_such_option=True)

    def test_get_config_returns_current(self):
        config = TermimatoConfig(default_speed=0.9)
        set_config(config)
        self.assertIs(get_config(), config)


if __name__ == "__main__":
    unittest.main()
