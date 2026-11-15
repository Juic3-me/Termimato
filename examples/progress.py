import asyncio

from termimato import Colors, ProgressAnimator


async def main():
    bar = ProgressAnimator(total=50, label="Copying", color=Colors.CYAN)
    drawing = asyncio.create_task(bar.start())

    for _ in range(50):
        await asyncio.sleep(0.05)
        bar.increment()

    await drawing
    await bar.complete()


if __name__ == "__main__":
    asyncio.run(main())
