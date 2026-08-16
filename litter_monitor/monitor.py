from __future__ import annotations

import asyncio
import logging

from pylitterbot import Account

from .config import Config, load_config
from .notifier import SmsNotifier
from .state import AlertState

logger = logging.getLogger(__name__)


def _check_condition(
    state: AlertState,
    notifier: SmsNotifier,
    robot_id: str,
    robot_name: str,
    condition: str,
    value: float,
    trigger_threshold: float,
    clear_threshold: float,
    is_low: bool,
    message: str,
) -> None:
    triggered = value <= trigger_threshold if is_low else value >= trigger_threshold
    cleared = value > clear_threshold if is_low else value < clear_threshold

    if triggered and not state.is_active(robot_id, condition):
        notifier.send(f"{robot_name}: {message} ({value:.0f}%)")
        state.set_active(robot_id, condition, True)
    elif cleared and state.is_active(robot_id, condition):
        state.set_active(robot_id, condition, False)


def check_robot(config: Config, state: AlertState, notifier: SmsNotifier, robot) -> None:
    robot_id = str(getattr(robot, "id", robot.name))

    waste_drawer_level = getattr(robot, "waste_drawer_level", None)
    if waste_drawer_level is not None:
        _check_condition(
            state,
            notifier,
            robot_id,
            robot.name,
            condition="drawer_full",
            value=waste_drawer_level,
            trigger_threshold=config.waste_drawer_full_threshold,
            clear_threshold=config.waste_drawer_full_threshold - config.alert_hysteresis,
            is_low=False,
            message="waste drawer is almost full",
        )

    litter_level = getattr(robot, "litter_level_calculated", None)
    if litter_level is None:
        litter_level = getattr(robot, "litter_level", None)
    if litter_level is not None:
        _check_condition(
            state,
            notifier,
            robot_id,
            robot.name,
            condition="litter_low",
            value=litter_level,
            trigger_threshold=config.litter_level_low_threshold,
            clear_threshold=config.litter_level_low_threshold + config.alert_hysteresis,
            is_low=True,
            message="litter is running low",
        )


async def run() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    config = load_config()
    state = AlertState(config.state_path)
    notifier = SmsNotifier(config)

    account = Account()
    await account.connect(
        username=config.littlerobot_username,
        password=config.litterrobot_password,
        load_robots=True,
    )

    if not account.robots:
        logger.warning("No Litter-Robot devices found on this account.")

    try:
        while True:
            try:
                await account.refresh_robots()
                for robot in account.robots:
                    check_robot(config, state, notifier, robot)
                state.save()
            except Exception:
                logger.exception("Error during poll cycle")

            await asyncio.sleep(config.poll_interval_minutes * 60)
    finally:
        await account.disconnect()


def main() -> None:
    asyncio.run(run())
