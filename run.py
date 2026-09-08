"""Ad-hoc browser-use runner.

    uv run python run.py "your task here" [--vision] [--model X] [--steps N]
"""

import argparse
import asyncio
import os
import shutil
from pathlib import Path

from dotenv import load_dotenv

from browser_use import Agent, Browser, ChatDeepSeek

load_dotenv(Path(__file__).with_name(".env"))

TEXT_MODEL = "deepseek-v4-pro"
VISION_MODEL = "deepseek-v4-flash-vision-exp"
SHOTS = Path(__file__).with_name("shots")


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("task", nargs="?", default=None)
    ap.add_argument("--task-file", default=None)
    ap.add_argument("--vision", action="store_true", help="send screenshots to the LLM")
    ap.add_argument("--model", default=None)
    ap.add_argument("--steps", type=int, default=15)
    ap.add_argument("--headful", action="store_true")
    ap.add_argument("--url", default=None,
                    help="navigate here deterministically before the agent starts")
    ap.add_argument("--profile", default=str(Path.home() / ".cache/browser-use-profile"),
                    help="persistent Chrome profile dir; keeps cookies between runs")
    args = ap.parse_args()

    task = Path(args.task_file).read_text() if args.task_file else args.task
    if not task:
        ap.error("give a task string or --task-file")

    model = args.model or (VISION_MODEL if args.vision else TEXT_MODEL)

    llm = ChatDeepSeek(
        model=model,
        api_key=os.environ["DEEPSEEK_API_KEY"],
        max_tokens=8000,  # reasoning tokens eat the budget; starve it and you get empty replies
    )

    browser = Browser(
        executable_path="/usr/bin/google-chrome",
        headless=not args.headful,
        user_data_dir=args.profile,
    )

    fallback = ChatDeepSeek(
        model=TEXT_MODEL if model != TEXT_MODEL else "deepseek-v4-flash",
        api_key=os.environ["DEEPSEEK_API_KEY"],
        max_tokens=8000,
    )

    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
        use_vision=args.vision,
        fallback_llm=fallback,
        initial_actions=[{"navigate": {"url": args.url, "new_tab": False}}] if args.url else None,
        llm_timeout=180,  # pro burns reasoning tokens; 90s default times out mid-thought
    )
    history = await agent.run(max_steps=args.steps)

    shutil.rmtree(SHOTS, ignore_errors=True)
    SHOTS.mkdir()
    for i, src in enumerate(p for p in history.screenshot_paths() if p):
        if Path(src).exists():
            shutil.copy(src, SHOTS / f"step_{i:02d}.png")

    print("\n=== MODEL ===", model, "| vision:", args.vision)
    print("=== URLS ===", " -> ".join(dict.fromkeys(u for u in history.urls() if u)))
    print("=== SHOTS ===", len(list(SHOTS.iterdir())), "in", SHOTS)
    print("=== RESULT ===")
    print(history.final_result())


if __name__ == "__main__":
    asyncio.run(main())
