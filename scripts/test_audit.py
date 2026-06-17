import asyncio

from app.core.dependencies import get_gap_detector

async def main():
    detector = get_gap_detector()

    result = await detector.detect(
        "employment survey",
        []
    )

    print(result)

if __name__ == "__main__":
    asyncio.run(main())