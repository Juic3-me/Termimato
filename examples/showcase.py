import asyncio

from termimato import (
    Colors,
    CountdownAnimator,
    Termimato,
    fade_out,
    glitch,
    particle_explosion,
    progress_bar,
    rainbow_text,
    scanner,
    type_writer,
)


async def main():
    async with Termimato() as t:
        await t.play(type_writer, "type_writer: text appears one character at a time", color=Colors.GREEN)
        await t.play(scanner, "scanner: a highlight runs across the line", bounce=True)
        await t.play(glitch, "glitch: the line falls apart for a moment", duration=1.5)
        await t.play(progress_bar, 20, prefix="progress_bar", speed=0.05)
        await t.play(rainbow_text, "rainbow_text: colors travel along the text", speed=0.03, cycle=False)
        await t.play(fade_out, "fade_out: the line disappears", effect="dissolve")
        await t.play(particle_explosion, "particle_explosion")
        await CountdownAnimator(seconds=3, final_message="Done").start()


if __name__ == "__main__":
    asyncio.run(main())
