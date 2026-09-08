import asyncio
import os

from dotenv import load_dotenv

from browser_use import Agent, Browser, ChatDeepSeek

load_dotenv()


async def main():
    llm = ChatDeepSeek(
        model="deepseek-v4-pro",
        api_key=os.environ["DEEPSEEK_API_KEY"],
    )

    browser = Browser(
        executable_path="/usr/bin/google-chrome",
        headless=True,
    )

    agent = Agent(
        task="Go to https://news.ycombinator.com and report the titles of the top 3 stories.",
        llm=llm,
        browser=browser,
        use_vision=False,  # DeepSeek is text-only; browser-use falls back to the DOM tree
    )

    result = await agent.run(max_steps=8)
    print("\n=== RESULT ===")
    print(result.final_result())


if __name__ == "__main__":
    asyncio.run(main())
