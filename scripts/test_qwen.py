# scripts/test_qwen.py

import asyncio

from app.ai.llm.qwen_client import QwenClient


async def main():
    client = QwenClient()

    response = await client.generate(
        system_prompt="You are a helpful assistant.",
        #user_prompt="Generate one survey question about employment."
        user_prompt="Questions about smartphone usage and internet connectivity."
    )

    print(response)


if __name__ == "__main__":
    asyncio.run(main())