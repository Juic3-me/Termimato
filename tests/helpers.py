import asyncio
import contextlib
import io
import unittest

from termimato import TermimatoConfig, reset_config, set_config


class OutputTestCase(unittest.TestCase):
    def setUp(self):
        set_config(TermimatoConfig(check_terminal_support=False))

    def tearDown(self):
        reset_config()

    def run_capture(self, coroutine):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            asyncio.run(coroutine)
        return buffer.getvalue()
