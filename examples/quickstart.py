import asyncio

from termimato import Colors, Termimato, type_writer


async def main():
    async with Termimato() as t:
        await t.play(type_writer, "Hello, World!", color=Colors.GREEN)

        spinner = await t.start_spinner("Processing...", color=Colors.CYAN)
        await asyncio.sleep(2)
        spinner.cancel()


if __name__ == "__main__":
    asyncio.run(main())
