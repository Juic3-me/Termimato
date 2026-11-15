import asyncio
import contextlib
import io
import re
import unittest

from termimato import (
    Colors,
    EffectNotFoundError,
    fade_out,
    glitch,
    particle_explosion,
    progress_bar,
    rainbow_text,
    scanner,
    type_writer,
    update_config,
)

from .helpers import OutputTestCase


class TypeWriterTest(OutputTestCase):
    def test_prints_every_character(self):
        out = self.run_capture(type_writer("hey", speed=0))
        plain = re.sub(r"\033\[[0-9;]*m", "", out)
        self.assertEqual(plain, "hey\n")

    def test_on_char_callback(self):
        seen = []
        self.run_capture(type_writer("abc", speed=0, on_char=seen.append))
        self.assertEqual(seen, ["a", "b", "c"])

    def test_uses_config_speed(self):
        update_config(default_speed=0)
        loop = asyncio.new_event_loop()
        started = loop.time()
        self.run_capture(type_writer("a" * 50))
        self.assertLess(loop.time() - started, 0.5)
        loop.close()


class ScannerTest(OutputTestCase):
    def window_sizes(self, text, **kwargs):
        out = self.run_capture(scanner(text, speed=0, **kwargs))
        pattern = re.escape(Colors.BOLD) + r".*?m(.*?)" + re.escape(Colors.RESET)
        return [len(match) for match in re.findall(pattern, out)]

    def test_odd_width(self):
        sizes = self.window_sizes("abcdefgh", width=3)
        self.assertEqual(sizes[3], 3)

    def test_even_width(self):
        sizes = self.window_sizes("abcdefgh", width=2)
        self.assertEqual(sizes[3], 2)

    def test_finishes_with_plain_text(self):
        out = self.run_capture(scanner("abc", speed=0))
        self.assertTrue(out.endswith("\rabc\n"))

    def test_bounce_does_not_repeat_the_ends(self):
        out = self.run_capture(scanner("abcd", speed=0, bounce=True))
        self.assertEqual(out.count("\r") - 1, 7)

    def test_empty_text(self):
        self.assertEqual(self.run_capture(scanner("", speed=0)), "\r\n")


class GlitchTest(OutputTestCase):
    def test_restores_text(self):
        out = self.run_capture(glitch("hello world", duration=0.15))
        self.assertTrue(out.endswith("\rhello world\n"))

    def test_zero_duration(self):
        out = self.run_capture(glitch("abc", duration=0))
        self.assertEqual(out, "\rabc\n")


class FadeOutTest(OutputTestCase):
    def test_unknown_effect_fails_before_output(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer), self.assertRaises(EffectNotFoundError):
            asyncio.run(fade_out("abc", effect="melt"))
        self.assertEqual(buffer.getvalue(), "")

    def test_every_effect_clears_the_line(self):
        for effect in ("dots", "fade", "dissolve", "vaporize"):
            with self.subTest(effect=effect):
                out = self.run_capture(fade_out("abcd", speed=0, effect=effect))
                self.assertTrue(out.endswith("\r    \r"))

    def test_fade_changes_shade(self):
        out = self.run_capture(fade_out("abcd", speed=0, effect="fade"))
        shades = set(re.findall(r"\033\[38;5;(\d+)m", out))
        self.assertEqual(len(shades), 11)
        self.assertIn("255", shades)
        self.assertIn("232", shades)

    def test_default_effect_from_config(self):
        update_config(fade_out_effect="dissolve")
        out = self.run_capture(fade_out("ab", speed=0))
        self.assertNotIn("·", out)


class ProgressBarTest(OutputTestCase):
    def test_complete_output(self):
        out = self.run_capture(progress_bar(5, speed=0, prefix="load"))
        self.assertIn("100.0%", out)
        self.assertIn("(5/5)", out)
        self.assertTrue(out.endswith("\n"))

    def test_zero_total_is_rejected(self):
        with self.assertRaises(ValueError):
            asyncio.run(progress_bar(0))

    def test_bar_is_full_at_the_end(self):
        out = self.run_capture(progress_bar(4, length=8, speed=0))
        self.assertIn("█" * 8, out)


class RainbowTest(OutputTestCase):
    def test_finite_run(self):
        out = self.run_capture(rainbow_text("abc", speed=0, cycle=False))
        self.assertTrue(out.endswith("\rabc\n"))
        self.assertNotIn("\033[38;2;0;0;0m", out)

    def test_cancel_restores_plain_text(self):
        async def scenario():
            task = asyncio.ensure_future(rainbow_text("abc", speed=0.01))
            await asyncio.sleep(0.05)
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task

        out = self.run_capture(scenario())
        self.assertTrue(out.endswith("\rabc\n"))


class ParticleTest(OutputTestCase):
    def test_uses_and_leaves_alternate_screen(self):
        out = self.run_capture(particle_explosion("boom", duration=0.12))
        self.assertTrue(out.startswith("\033[?1049h"))
        self.assertTrue(out.endswith("\033[?1049l"))
        self.assertIn("\033[2J", out)

    def test_leaves_screen_when_cancelled(self):
        async def scenario():
            task = asyncio.ensure_future(particle_explosion("boom", duration=5))
            await asyncio.sleep(0.1)
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)

        out = self.run_capture(scenario())
        self.assertTrue(out.endswith("\033[?1049l"))


if __name__ == "__main__":
    unittest.main()
