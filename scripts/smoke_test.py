"""Verifies a deployment is actually working: logs into Whisker, reads real
robot status, and (optionally) sends a real test text through the SMS
gateway. Run this once after deploying to confirm everything is wired up.

Usage:
    python scripts/smoke_test.py            # checks Whisker login + robot status only
    python scripts/smoke_test.py --notify    # also sends a real test text
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from pylitterbot import Account

sys.path.insert(0, ".")

from litter_monitor.config import load_config
from litter_monitor.notifier import SmsNotifier


async def main(send_test_text: bool) -> int:
    config = load_config()

    print("Connecting to Whisker account...")
    account = Account()
    try:
        await account.connect(
            username=config.littlerobot_username,
            password=config.litterrobot_password,
            load_robots=True,
        )
    except Exception as exc:
        print(f"FAILED: could not log into Whisker: {exc}")
        return 1

    if not account.robots:
        print("FAILED: logged in, but no robots found on this account.")
        await account.disconnect()
        return 1

    for robot in account.robots:
        waste = getattr(robot, "waste_drawer_level", None)
        litter = getattr(robot, "litter_level_calculated", None) or getattr(robot, "litter_level", None)
        print(f"OK: {robot.name} -> waste_drawer_level={waste}, litter_level={litter}")

    await account.disconnect()

    if send_test_text:
        print("Sending test text via SMS gateway...")
        try:
            SmsNotifier(config).send("Litter-Robot monitor: smoke test successful.")
        except Exception as exc:
            print(f"FAILED: could not send test text: {exc}")
            return 1
        print("OK: test text sent, check your phone.")

    print("Smoke test passed.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--notify", action="store_true", help="also send a real test text")
    args = parser.parse_args()
    sys.exit(asyncio.run(main(args.notify)))
