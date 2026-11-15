import asyncio
import re
import unittest

from termimato import (
    AnimationController,
    AnimationError,
    AnimationState,
    ColorTheme,
    CountdownAnimator,
    ProgressAnimator,
    SpinnerAnimator,
    TerminalError,
    TextAnimator,
    Termimato,
    TermimatoConfig,
    set_config,
    fade_out,
    type_writer,
)

from .helpers import OutputTestCase


class SpinnerTest(OutputTestCase):
    def test_stop_ends_cleanly(self):
        async def scenario():
            spinner = SpinnerAnimator(label="work", interval=0.01)
            task = asyncio.ensure_future(spinner.start())
            await asyncio.sleep(0.08)
            await spinner.stop()
            await task
            return spinner

        buffer_state = {}

        async def wrapper():
            buffer_state["spinner"] = await scenario()

        out = self.run_capture(wrapper())
        spinner = buffer_state["spinner"]
        self.assertEqual(spinner.state, AnimationState.CANCELLED)
        self.assertGreater(spinner.metrics.frame_count, 2)
        self.assertIn("work", out)
        self.assertTrue(out.endswith("\r\033[K"))

    def test_stop_before_start_is_harmless(self):
        spinner = SpinnerAnimator()
        asyncio.run(spinner.stop())
        self.assertEqual(spinner.state, AnimationState.IDLE)

    def test_pause_and_resume(self):
        async def scenario():
            spinner = SpinnerAnimator(interval=0.01)
            task = asyncio.ensure_future(spinner.start())
            await asyncio.sleep(0.05)
            await spinner.pause()
            paused = spinner.state
            frames = spinner.metrics.frame_count
            await asyncio.sleep(0.15)
            still = spinner.metrics.frame_count
            await spinner.resume()
            await asyncio.sleep(0.05)
            resumed = spinner.metrics.frame_count
            await spinner.stop()
            await task
            return paused, frames, still, resumed

        results = {}

        async def wrapper():
            results["r"] = await scenario()

        self.run_capture(wrapper())
        paused, frames, still, resumed = results["r"]
        self.assertEqual(paused, AnimationState.PAUSED)
        self.assertLessEqual(still - frames, 1)
        self.assertGreater(resumed, still)

    def test_cannot_start_twice(self):
        async def scenario():
            spinner = SpinnerAnimator(interval=0.01)
            task = asyncio.ensure_future(spinner.start())
            await asyncio.sleep(0.03)
            with self.assertRaises(AnimationError):
                await spinner.start()
            await spinner.stop()
            await task

        self.run_capture(scenario())


class ProgressTest(OutputTestCase):
    def test_runs_until_complete(self):
        async def scenario():
            bar = ProgressAnimator(total=4, label="copy", width=8)
            task = asyncio.ensure_future(bar.start())
            for _ in range(4):
                await asyncio.sleep(0.02)
                bar.increment()
            await task
            await bar.complete()
            return bar

        holder = {}

        async def wrapper():
            holder["bar"] = await scenario()

        out = self.run_capture(wrapper())
        self.assertEqual(holder["bar"].state, AnimationState.COMPLETED)
        self.assertIn("100.0%", out)
        self.assertIn("copy completed", out)

    def test_update_is_clamped(self):
        bar = ProgressAnimator(total=10)
        bar.update(50)
        self.assertEqual(bar.current, 10)
        bar.update(-4)
        self.assertEqual(bar.current, 0)

    def test_zero_total(self):
        bar = ProgressAnimator(total=0)
        out = self.run_capture(bar.start())
        self.assertIn("100.0%", out)


class CountdownTest(OutputTestCase):
    def test_last_number_is_visible_for_a_second(self):
        async def scenario():
            loop = asyncio.get_running_loop()
            started = loop.time()
            await CountdownAnimator(seconds=2).start()
            return loop.time() - started

        holder = {}

        async def wrapper():
            holder["elapsed"] = await scenario()

        out = self.run_capture(wrapper())
        self.assertGreaterEqual(holder["elapsed"], 1.9)
        numbers = re.findall(r"\r\033\[[0-9;]*m(\d\d)", out)
        self.assertEqual(numbers, ["02", "01"])
        self.assertIn("GO!", out)

    def test_clock_parts(self):
        countdown = CountdownAnimator(seconds=3725, format_string="{hours}:{formatted_minutes}:{formatted_seconds}")
        countdown.current_second = 3725
        out = self.run_capture(self._render(countdown))
        self.assertIn("1:02:05", out)

    @staticmethod
    async def _render(countdown):
        countdown._render_frame()


class TextAnimatorTest(OutputTestCase):
    def test_wraps_effect(self):
        async def scenario():
            animator = TextAnimator("hi", lambda text: type_writer(text, speed=0), "Typing")
            await animator.start()
            return animator.state

        holder = {}

        async def wrapper():
            holder["state"] = await scenario()

        self.run_capture(wrapper())
        self.assertEqual(holder["state"], AnimationState.COMPLETED)

    def test_failure_is_wrapped(self):
        async def broken(text):
            raise RuntimeError("boom")

        animator = TextAnimator("x", broken)
        with self.assertRaises(AnimationError) as caught:
            asyncio.run(animator.start())
        self.assertEqual(animator.state, AnimationState.ERROR)
        self.assertIn("boom", str(caught.exception))


class TermimatoTest(OutputTestCase):
    def test_hides_and_restores_cursor(self):
        async def scenario():
            async with Termimato():
                pass

        out = self.run_capture(scenario())
        self.assertEqual(out, "\033[?25l\033[?25h")

    def test_cursor_restored_after_error(self):
        async def scenario():
            with self.assertRaises(ZeroDivisionError):
                async with Termimato():
                    1 / 0

        out = self.run_capture(scenario())
        self.assertTrue(out.endswith("\033[?25h"))

    def test_requires_terminal(self):
        set_config(TermimatoConfig(check_terminal_support=True))

        async def scenario():
            async with Termimato():
                pass

        with self.assertRaises(TerminalError):
            asyncio.run(scenario())

    def test_play_runs_effect(self):
        async def scenario():
            async with Termimato() as t:
                await t.play(type_writer, "ok", speed=0)

        out = self.run_capture(scenario())
        self.assertIn("o", out)
        self.assertIn("k", out)

    def test_play_passes_effect_keyword(self):
        async def scenario():
            async with Termimato() as t:
                await t.play(fade_out, "ab", speed=0, effect="dissolve")

        out = self.run_capture(scenario())
        self.assertIn("\r  \r", out)

    def test_play_wraps_errors(self):
        async def effect():
            raise ValueError("bad value")

        async def scenario():
            async with Termimato() as t:
                with self.assertRaises(AnimationError) as caught:
                    await t.play(effect)
                self.assertEqual(caught.exception.effect_name, "effect")

        self.run_capture(scenario())

    def test_spinner_from_readme_example(self):
        async def scenario():
            async with Termimato() as t:
                spinner = await t.start_spinner("Processing...")
                await asyncio.sleep(0.15)
                spinner.cancel()

        out = self.run_capture(scenario())
        self.assertIn("Processing...", out)
        self.assertTrue(out.endswith("\r\033[K\033[?25h"))

    def test_exit_cancels_running_spinner(self):
        async def scenario():
            async with Termimato() as t:
                await t.start_spinner("left running")
                await asyncio.sleep(0.05)
            return t.controller.active

        holder = {}

        async def wrapper():
            holder["active"] = await scenario()

        self.run_capture(wrapper())
        self.assertEqual(holder["active"], 0)

    def test_theme_by_name_and_instance(self):
        self.assertEqual(Termimato(theme="light").theme, ColorTheme.light())
        self.assertEqual(Termimato(theme=ColorTheme.rainbow()).theme, ColorTheme.rainbow())
        self.assertEqual(Termimato().theme, ColorTheme.dark())


class ControllerTest(OutputTestCase):
    def test_limit(self):
        async def scenario():
            controller = AnimationController(limit=1)
            first = controller.spawn(asyncio.sleep(1))
            with self.assertRaises(AnimationError):
                controller.spawn(asyncio.sleep(1))
            await controller.cancel_all()
            return first.cancelled(), controller.active

        holder = {}

        async def wrapper():
            holder["r"] = await scenario()

        self.run_capture(wrapper())
        self.assertEqual(holder["r"], (True, 0))


if __name__ == "__main__":
    unittest.main()
